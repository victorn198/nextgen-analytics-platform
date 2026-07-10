import { cp, mkdir, readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";

const root = new URL("../", import.meta.url).pathname.replace(/^\/(.:)/, "$1");
const reportDir = join(root, "powerbi", "OpenSourceLandscape", "OpenSourceLandscape.Report");
const definitionDir = join(reportDir, "definition");
const pagesDir = join(definitionDir, "pages");
const sourcePage = "7a9c20e5d8414f6b93c1";
const pages = [
  { id: sourcePage, name: "Executive Overview", title: "Executive Overview | Open Source Demand", subtitle: "A business view of community demand, supply and portfolio opportunity." },
  { id: "8b0d31f6e9524a7c04d2", name: "Market Demand", title: "Market Demand | Where Attention Is Concentrated", subtitle: "Compare technology segments and identify categories with visible market pull." },
  { id: "9c1e42a7f0635b8d15e3", name: "Opportunity Queue", title: "Opportunity Queue | Repositories Worth Reviewing", subtitle: "Prioritized evidence for commercial research, partnerships and technical scouting." },
];

const readJson = async (path) => JSON.parse(await readFile(path, "utf8"));
const writeJson = async (path, payload) => writeFile(path, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
const literal = (value) => ({ expr: { Literal: { Value: value } } });
const color = (value) => ({ solid: { color: literal(`'${value}'`) } });
const position = (x, y, width, height, z) => ({ x, y, z, width, height, tabOrder: z });

const pagesMetadata = await readJson(join(pagesDir, "pages.json"));
for (const page of pages.slice(1)) {
  await cp(join(pagesDir, sourcePage), join(pagesDir, page.id), { recursive: true });
}

const pageVisuals = async (page) => {
  const pagePath = join(pagesDir, page.id);
  const pageJsonPath = join(pagePath, "page.json");
  const pageJson = await readJson(pageJsonPath);
  pageJson.name = page.id;
  pageJson.displayName = page.name;
  await writeJson(pageJsonPath, pageJson);

  const visualsPath = join(pagePath, "visuals");
  const visualIds = [
    "01a4b8c2d6e0f3a7b9c1",
    "12b5c9d3e7f1a4b8c0d2",
    "23c6d0e4f8a2b5c9d1e3",
    "34d7e1f5a9b3c6d0e2f4",
    "45e8f2a6b0c4d7e1f3a5",
    "56f9a3b7c1d5e8f2a4b6",
  ];
  for (const id of visualIds) {
    const path = join(visualsPath, id, "visual.json");
    const visual = await readJson(path);
    if (id === visualIds[0]) {
      const paragraphs = visual.visual.objects.general[0].properties.paragraphs;
      paragraphs[0].textRuns[0].value = page.title;
      paragraphs[1].textRuns[0].value = page.subtitle;
      visual.position = position(264, 24, 1080, 72, 1000);
    }
    if (id === visualIds[3]) visual.position = position(264, 120, 1624, 128, 4000);
    if (id === visualIds[4]) visual.position = position(264, 280, 640, 760, 5000);
    if (id === visualIds[5]) visual.position = position(928, 280, 960, 760, 6000);
    await writeJson(path, visual);
  }

  const navId = "a1b2c3d4e5f60718293a";
  const navPath = join(visualsPath, navId);
  await mkdir(navPath, { recursive: true });
  await writeJson(join(navPath, "visual.json"), {
    $schema: "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.9.0/schema.json",
    name: navId,
    position: position(16, 144, 216, 520, 9000),
    visual: {
      visualType: "pageNavigator",
      objects: {
        layout: [{ properties: { orientation: literal("1L"), rowCount: literal("3L"), columnCount: literal("1L"), cellPadding: literal("8L") } }],
        text: [
          { selector: { id: "default" }, properties: { show: literal("true"), fontFamily: literal("'Segoe UI'"), fontSize: literal("11D"), fontColor: color("#334155"), horizontalAlignment: literal("'left'") } },
          { selector: { id: "selected" }, properties: { show: literal("true"), bold: literal("true"), fontColor: color("#FFFFFF") } },
        ],
        fill: [
          { selector: { id: "default" }, properties: { show: literal("true"), fillColor: color("#FFFFFF"), transparency: literal("0D") } },
          { selector: { id: "selected" }, properties: { show: literal("true"), fillColor: color("#087EA4"), transparency: literal("0D") } },
          { selector: { id: "hover" }, properties: { show: literal("true"), fillColor: color("#E0F2FE"), transparency: literal("0D") } },
        ],
        outline: [{ selector: { id: "default" }, properties: { show: literal("true") } }],
        shape: [{ properties: { tileShape: literal("'rectangleRounded'") } }],
        accentBar: [{ selector: { id: "selected" }, properties: { show: literal("true"), color: color("#F59E0B") } }],
      },
      visualContainerObjects: {
        background: [{ properties: { show: literal("true"), color: color("#FFFFFF"), transparency: literal("0D") } }],
        border: [{ properties: { show: literal("true"), color: color("#E2E8F0"), radius: literal("6L") } }],
        padding: [{ properties: { top: literal("8L"), bottom: literal("8L"), left: literal("8L"), right: literal("8L") } }],
      },
    },
  });
};

for (const page of pages) await pageVisuals(page);
pagesMetadata.pageOrder = pages.map((page) => page.id);
pagesMetadata.activePageName = sourcePage;
await writeJson(join(pagesDir, "pages.json"), pagesMetadata);
console.log(`Added business navigation and ${pages.length} pages.`);
