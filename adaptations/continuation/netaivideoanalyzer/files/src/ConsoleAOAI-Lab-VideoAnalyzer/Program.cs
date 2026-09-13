// MCAPS continuation lab variant of ConsoleAOAI-04-VideoAnalyzer.
//
// Differences from the native sample, all documented as lab adaptations:
//   1. Entra ID (DefaultAzureCredential) instead of a user-secrets API key, so
//      no key is ever persisted to disk.
//   2. Non-streaming completion so that token usage is returned reliably.
//   3. Per-call telemetry written to a JSON file for the measurement contract.
//   4. Video file, prompt, frame count and test label are parameterised so the
//      same native sampling shape can be reused for negative tests.
// The OpenCV frame-extraction and frame-sampling logic is unchanged.

using System.Diagnostics;
using System.Text.Json;
using Azure.AI.OpenAI;
using Azure.Identity;
using OpenAI.Chat;
using OpenCvSharp;

if (Environment.GetEnvironmentVariable("LAB_ALLOW_PROVIDER_CALLS") != "1"
    || !int.TryParse(Environment.GetEnvironmentVariable("LAB_ATTEMPT_BUDGET"), out var approvedBudget)
    || approvedBudget <= 0)
{
    throw new InvalidOperationException("Archived harness is disarmed; provider execution requires separate approval.");
}

string videoFile = GetArg("--video") ?? VideosHelper.GetVideoFilePathFireTruck();
string? videoFile2 = GetArg("--video2");
string label = GetArg("--label") ?? "unlabelled";
string prompt = GetArg("--prompt") ?? PromptsHelper.UserPromptDescribeVideo;
int numberOfFrames = int.TryParse(GetArg("--frames"), out var nf) ? nf : PromptsHelper.NumberOfFrames;
string outFile = GetArg("--out") ?? $"lab-video-{label}.json";

string endpoint = Environment.GetEnvironmentVariable("LAB_AOAI_ENDPOINT")
                  ?? throw new InvalidOperationException("LAB_AOAI_ENDPOINT is required");
string modelId = Environment.GetEnvironmentVariable("LAB_AOAI_MODEL")
                 ?? throw new InvalidOperationException("LAB_AOAI_MODEL is required");

var telemetry = new Dictionary<string, object?>
{
    ["label"] = label,
    ["timestamp_utc"] = DateTime.UtcNow.ToString("o"),
    ["endpoint"] = endpoint,
    ["requested_model"] = modelId,
    ["video_file"] = Path.GetFileName(videoFile),
    ["requested_frames"] = numberOfFrames,
    ["prompt_chars"] = prompt.Length,
    ["auth"] = "entra-default-azure-credential",
};

var frames = new List<Mat>();
string? extractionError = null;
try
{
    frames.AddRange(Decode(videoFile));
}
catch (Exception ex)
{
    extractionError = $"{ex.GetType().Name}: {ex.Message}";
}

var frames2 = new List<Mat>();
if (videoFile2 is not null)
{
    try { frames2.AddRange(Decode(videoFile2)); }
    catch (Exception ex) { extractionError = $"{ex.GetType().Name}: {ex.Message}"; }
    telemetry["video_file_2"] = Path.GetFileName(videoFile2);
    telemetry["frames_decoded_2"] = frames2.Count;
}

static List<Mat> Decode(string path)
{
    var list = new List<Mat>();
    var video = new VideoCapture(path);
    while (video.IsOpened())
    {
        var frame = new Mat();
        if (!video.Read(frame) || frame.Empty()) break;
        if (frame.Width > 800)
            Cv2.Resize(frame, frame, new OpenCvSharp.Size(frame.Width / 2, frame.Height / 2));
        list.Add(frame);
    }
    video.Release();
    return list;
}

telemetry["frames_decoded"] = frames.Count;
telemetry["decode_error"] = extractionError;

if (frames.Count == 0)
{
    // Corrupted / undecodable media must fail before any paid model call.
    telemetry["outcome"] = "decode_failed_no_model_call";
    telemetry["model_attempts"] = 0;
    Write(outFile, telemetry);
    Console.WriteLine($"[lab] decode failed for {videoFile}; no model call issued.");
    return;
}

string dataFolderPath = Path.Combine(Directory.GetCurrentDirectory(), $"data-{label}");
if (Directory.Exists(dataFolderPath)) Directory.Delete(dataFolderPath, true);
Directory.CreateDirectory(Path.Combine(dataFolderPath, "frames"));

var messages = new List<ChatMessage>
{
    new SystemChatMessage(PromptsHelper.SystemPrompt),
    new UserChatMessage(prompt),
};

int step = (int)Math.Ceiling((double)frames.Count / numberOfFrames);
int submitted = 0;
long frameBytes = 0;
var frameIndexes = new List<int>();
for (int i = 0; i < frames.Count; i += step)
{
    string framePath = Path.Combine(dataFolderPath, "frames", $"{i:D5}.jpg");
    Cv2.ImWrite(framePath, frames[i]);
    var bytes = File.ReadAllBytes(framePath);
    frameBytes += bytes.Length;
    messages.Add(new UserChatMessage(ChatMessageContentPart.CreateImagePart(
        imageBytes: BinaryData.FromBytes(bytes), imageBytesMediaType: "image/jpeg")));
    frameIndexes.Add(i);
    submitted++;
}

telemetry["frame_sampling_step"] = step;
telemetry["frames_submitted"] = submitted;
telemetry["frame_indexes"] = frameIndexes;
telemetry["frame_bytes_total"] = frameBytes;

if (frames2.Count > 0)
{
    messages.Add(new UserChatMessage("The frames above are from CLIP A. The frames below are from CLIP B."));
    int step2 = (int)Math.Ceiling((double)frames2.Count / numberOfFrames);
    int submitted2 = 0;
    for (int i = 0; i < frames2.Count; i += step2)
    {
        string framePath = Path.Combine(dataFolderPath, "frames", $"b{i:D5}.jpg");
        Cv2.ImWrite(framePath, frames2[i]);
        var bytes = File.ReadAllBytes(framePath);
        frameBytes += bytes.Length;
        messages.Add(new UserChatMessage(ChatMessageContentPart.CreateImagePart(
            imageBytes: BinaryData.FromBytes(bytes), imageBytesMediaType: "image/jpeg")));
        submitted2++;
    }
    telemetry["frames_submitted_2"] = submitted2;
    telemetry["frame_bytes_total"] = frameBytes;
}

var client = new AzureOpenAIClient(new Uri(endpoint), new DefaultAzureCredential());
var chatClient = client.GetChatClient(modelId);

var sw = Stopwatch.StartNew();
try
{
    var completion = await chatClient.CompleteChatAsync(messages);
    sw.Stop();
    var value = completion.Value;
    telemetry["outcome"] = "response";
    telemetry["http_status"] = 200;
    telemetry["provider_response_id"] = value.Id;
    telemetry["served_model"] = value.Model;
    telemetry["finish_reason"] = value.FinishReason.ToString();
    telemetry["refusal"] = value.Refusal;
    telemetry["input_tokens"] = value.Usage?.InputTokenCount;
    telemetry["output_tokens"] = value.Usage?.OutputTokenCount;
    telemetry["total_tokens"] = value.Usage?.TotalTokenCount;
    telemetry["cached_tokens"] = null; // not exposed by Azure.AI.OpenAI 2.0.0 pinned by the sample
    telemetry["reasoning_tokens"] = value.Usage?.OutputTokenDetails?.ReasoningTokenCount;
    telemetry["client_elapsed_s"] = Math.Round(sw.Elapsed.TotalSeconds, 4);
    telemetry["model_attempts"] = 1;
    string text = string.Join("", value.Content.Select(c => c.Text));
    telemetry["response_text"] = text;
    Console.WriteLine(text);
}
catch (Exception ex)
{
    sw.Stop();
    telemetry["outcome"] = "exception";
    telemetry["exception_type"] = ex.GetType().Name;
    telemetry["message"] = ex.Message;
    telemetry["client_elapsed_s"] = Math.Round(sw.Elapsed.TotalSeconds, 4);
    telemetry["model_attempts"] = 1;
    Console.WriteLine($"[lab] model call failed: {ex.GetType().Name}: {ex.Message}");
}

Write(outFile, telemetry);

static void Write(string path, Dictionary<string, object?> data)
{
    File.WriteAllText(path, JsonSerializer.Serialize(data, new JsonSerializerOptions { WriteIndented = true }));
    Console.WriteLine($"\n[lab] telemetry written to {Path.GetFullPath(path)}");
}

static string? GetArg(string name)
{
    var argv = Environment.GetCommandLineArgs();
    for (int i = 0; i < argv.Length - 1; i++)
        if (argv[i] == name) return argv[i + 1];
    return null;
}
