import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SCRIPTS = Path(__file__).resolve().parents[1]
SHELL = shutil.which("pwsh") or shutil.which("powershell")


@unittest.skipUnless(SHELL, "PowerShell is required for the real script fixture")
class CloudLifecycleTests(unittest.TestCase):
    def test_stop_deactivates_older_running_revision_without_deploying(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            (root / "evidence" / "content").mkdir(parents=True)
            shutil.copy2(SCRIPTS / "Stop-ContentCloud.ps1", root / "scripts")
            (root / "Invoke-LabAz.ps1").write_text(
                r"""param([string[]]$AzArguments)
$global:LASTEXITCODE=0
$command=$AzArguments[0..2] -join ' '
$global:calls += $command
switch ($command) {
 'containerapp revision list' {
  if ($AzArguments -notcontains '--all') { throw 'All revisions must be checked' }
  @(
   @{name='older-ready'; properties=@{active=(-not $global:stopped);replicas=$(if($global:stopped){0}else{1});runningState='Test'}}
   @{name='latest-empty'; properties=@{active=$false;replicas=0;runningState='Stopped'}}
  ) | ConvertTo-Json -Depth 5
 }
 'containerapp revision deactivate' {
  $index=[array]::IndexOf($AzArguments,'--revision')
  if ($AzArguments[$index+1] -ne 'older-ready') { throw 'Wrong revision' }
  $global:stopped=$true
 }
 default { throw "Unexpected mutation: $command" }
}
""",
                encoding="utf-8",
            )
            runner = root / "test.ps1"
            runner.write_text(
                r"""$ErrorActionPreference='Stop'
$global:calls=@()
$global:stopped=$false
& (Join-Path $PSScriptRoot 'scripts\Stop-ContentCloud.ps1') -Service api
if (-not $global:stopped) { throw 'Older live revision was not stopped' }
if ($global:calls.Count -ne 3) { throw 'Unexpected command count' }
""",
                encoding="utf-8",
            )
            run = subprocess.run(
                [SHELL, "-NoProfile", "-NonInteractive", "-File", str(runner)],
                capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            evidence = json.loads(
                (root / "evidence" / "content" / "cloud-stop-api-all-revisions.json")
                .read_text(encoding="utf-8-sig")
            )
            self.assertEqual(evidence["services"][0]["replicas"], 0)
            self.assertEqual(len(evidence["services"][0]["revisions"]), 2)

    def test_deployment_hold_fails_before_any_azure_or_build_action(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            evidence = root / "evidence" / "content"
            evidence.mkdir(parents=True)
            (evidence / "result.json").write_text(
                json.dumps({"modelCallsOnHold": True}), encoding="utf-8"
            )
            shutil.copy2(SCRIPTS / "Deploy-ContentCloud.ps1", root / "scripts")
            run = subprocess.run(
                [SHELL, "-NoProfile", "-NonInteractive", "-File",
                 str(root / "scripts" / "Deploy-ContentCloud.ps1"),
                 "-Service", "processor", "-WarmForTest", "-PauseWorkers"],
                capture_output=True, text=True, timeout=30,
            )
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("on inference hold", run.stderr)
            self.assertNotIn("not recognized", run.stderr)


if __name__ == "__main__":
    unittest.main()
