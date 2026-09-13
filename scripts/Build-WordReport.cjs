const fs = require("node:fs");
const path = require("node:path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, PageNumber, HeadingLevel, WidthType, ShadingType,
  BorderStyle, AlignmentType, LevelFormat, ExternalHyperlink,
} = require("docx");

const [input, output] = process.argv.slice(2);
if (!input || !output) {
  throw new Error("Usage: node Build-WordReport.cjs <report.md> <report.docx>");
}
const lines = fs.readFileSync(input, "utf8").replace(/\r\n/g, "\n").split("\n");
const children = [];
const numbering = [
  {
    reference: "bullets",
    levels: [{
      level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 360, hanging: 180 } } },
    }],
  },
];
let numberedList = null;
let listCount = 0;

function runs(text, size = 21) {
  const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`|https?:\/\/[^\s)]+)/g).filter(Boolean);
  return parts.map((part) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return new TextRun({ text: part.slice(2, -2), bold: true, size });
    }
    if (part.startsWith("`") && part.endsWith("`")) {
      return new TextRun({ text: part.slice(1, -1), font: "Consolas", size: size - 1 });
    }
    if (/^https?:\/\//.test(part)) {
      return new ExternalHyperlink({
        link: part,
        children: [new TextRun({ text: part, style: "Hyperlink", size })],
      });
    }
    return new TextRun({ text: part, size });
  });
}

function tableRows(rows) {
  const parsed = rows
    .filter((line) => !/^\|(?:\s*:?-+:?\s*\|)+\s*$/.test(line))
    .map((line) => line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((cell) => cell.trim()));
  const count = parsed[0].length;
  if (parsed.some((row) => row.length !== count)) {
    throw new Error(`Inconsistent table column count: ${rows[0]}`);
  }
  const widths = Array(count).fill(Math.floor(9360 / count));
  widths[count - 1] += 9360 - widths.reduce((sum, width) => sum + width, 0);
  const border = { style: BorderStyle.SINGLE, size: 1, color: "CBD5E1" };
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: widths,
    rows: parsed.map((cells, index) => new TableRow({
      tableHeader: index === 0,
      children: cells.map((text, col) => new TableCell({
        width: { size: widths[col], type: WidthType.DXA },
        margins: { top: 90, bottom: 90, left: 100, right: 100 },
        borders: { top: border, bottom: border, left: border, right: border },
        shading: { type: ShadingType.CLEAR, fill: index === 0 ? "E2E8F0" : "FFFFFF" },
        children: [new Paragraph({
          spacing: { after: 30 },
          children: runs(index === 0 ? `**${text}**` : text, count > 4 ? 17 : 19),
        })],
      })),
    })),
  });
}

for (let i = 0; i < lines.length; i += 1) {
  const line = lines[i];
  if (!line.trim()) {
    numberedList = null;
    continue;
  }
  if (line.startsWith("```")) {
    numberedList = null;
    while (++i < lines.length && !lines[i].startsWith("```")) {
      children.push(new Paragraph({
        shading: { type: ShadingType.CLEAR, fill: "F1F5F9" },
        spacing: { after: 0 },
        children: [new TextRun({ text: lines[i] || " ", font: "Consolas", size: 17 })],
      }));
    }
    children.push(new Paragraph({ spacing: { after: 80 } }));
    continue;
  }
  if (line.startsWith("|")) {
    const rows = [line];
    while (i + 1 < lines.length && lines[i + 1].startsWith("|")) rows.push(lines[++i]);
    children.push(tableRows(rows), new Paragraph({ spacing: { after: 70 } }));
    continue;
  }
  const heading = /^(#{1,3}) (.+)$/.exec(line);
  if (heading) {
    const levels = [HeadingLevel.HEADING_1, HeadingLevel.HEADING_2, HeadingLevel.HEADING_3];
    children.push(new Paragraph({
      heading: levels[heading[1].length - 1],
      children: runs(heading[2], heading[1].length === 1 ? 32 : 26),
    }));
    continue;
  }
  if (/^- /.test(line)) {
    children.push(new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: runs(line.slice(2)) }));
    continue;
  }
  if (/^\d+\. /.test(line)) {
    if (!numberedList) {
      numberedList = `numbered-${++listCount}`;
      numbering.push({
        reference: numberedList,
        levels: [{
          level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 360, hanging: 180 } } },
        }],
      });
    }
    children.push(new Paragraph({
      numbering: { reference: numberedList, level: 0 },
      children: runs(line.replace(/^\d+\. /, "")),
    }));
    continue;
  }
  children.push(new Paragraph({ children: runs(line) }));
}

const doc = new Document({
  creator: "PTU Bundle Accelerator",
  title: "MCAPS PTU Bundle Accelerator Evaluation",
  description: "Evidence-based functionality, model consumption, infrastructure and cost report.",
  numbering: { config: numbering },
  styles: {
    default: {
      document: {
        run: { font: "Arial", size: 21 },
        paragraph: { spacing: { after: 120 } },
      },
    },
    paragraphStyles: [1, 2, 3].map((level) => ({
      id: `Heading${level}`, name: `Heading ${level}`, basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { font: "Arial", color: "000000", bold: true, size: level === 1 ? 32 : 26 },
      paragraph: { outlineLevel: level - 1, keepNext: true, spacing: { before: 240, after: 120 } },
    })),
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1200, bottom: 1200, left: 1440, right: 1440 },
      },
    },
    headers: { default: new Header({ children: [new Paragraph({
      children: [new TextRun({ text: "PTU BUNDLE ACCELERATOR | MCAPS LAB", size: 17, color: "475569" })],
    })] }) },
    footers: { default: new Footer({ children: [new Paragraph({
      alignment: AlignmentType.RIGHT,
      children: [
        new TextRun({ text: "Synthetic-data evaluation | Page ", size: 17 }),
        new TextRun({ children: [PageNumber.CURRENT], size: 17 }),
      ],
    })] }) },
    children,
  }],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.mkdirSync(path.dirname(path.resolve(output)), { recursive: true });
  fs.writeFileSync(output, buffer);
  console.log(`Created ${output} (${buffer.length} bytes)`);
}).catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
