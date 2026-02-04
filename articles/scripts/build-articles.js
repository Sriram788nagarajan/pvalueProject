import fs from "fs-extra";
import matter from "gray-matter";
import MarkdownIt from "markdown-it";
import path from "path";

// Initialize Markdown parser
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
});

// ===== PATH CONFIGURATION =====

// Source markdown article
const ARTICLE_SRC =
  "articles/supporting/sample-size-power-mde/why-underpowered-tests-fail.md";

// Shared HTML layout
const LAYOUT_PATH =
  "articles/shared/article_layout.html";

// Output directory (final static HTML)
const OUTPUT_DIR =
  "public/articles/why-underpowered-tests-fail";

// ===== BUILD FUNCTION =====

async function buildArticle() {
  // 1. Read markdown file
  const rawMarkdown = await fs.readFile(ARTICLE_SRC, "utf8");

  // 2. Parse front-matter
  const { data, content } = matter(rawMarkdown);

  if (!data.title || !data.description) {
    throw new Error("Front-matter must include title and description");
  }

  // 3. Convert markdown → HTML
  const renderedContent = md.render(content);

  // 4. Read shared HTML layout
  const layout = await fs.readFile(LAYOUT_PATH, "utf8");

  // 5. Inject content into layout
  const finalHtml = layout
    .replaceAll("{{title}}", data.title)
    .replaceAll("{{description}}", data.description)
    .replace("{{content}}", renderedContent);

  // 6. Ensure output directory exists
  await fs.ensureDir(OUTPUT_DIR);

  // 7. Write final HTML file
  const outputPath = path.join(OUTPUT_DIR, "index.html");
  await fs.writeFile(outputPath, finalHtml, "utf8");

  console.log("Article built successfully:");
  console.log("   →", outputPath);
}

// Run build
buildArticle().catch((err) => {
  console.error("Article build failed:");
  console.error(err);
});
