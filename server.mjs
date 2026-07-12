import { createServer } from "node:http";
import { readFile, existsSync, statSync } from "node:fs";
import { join, extname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = fileURLToPath(new URL(".", import.meta.url));
const clientDir = join(__dirname, "dist", "client");

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".js": "application/javascript",
  ".css": "text/css",
  ".json": "application/json",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".svg": "image/svg+xml",
  ".ico": "image/x-icon",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
  ".ttf": "font/ttf",
};

const MAX_BODY_BYTES = 1024 * 1024; // 1 MB

const handler = (await import("./dist/server/server.js")).default;

function readBody(nodeReq) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    let total = 0;
    nodeReq.on("data", (c) => {
      total += c.length;
      if (total > MAX_BODY_BYTES) {
        nodeReq.destroy();
        reject(new Error("Body too large"));
        return;
      }
      chunks.push(c);
    });
    nodeReq.on("end", () => resolve(Buffer.concat(chunks)));
    nodeReq.on("error", reject);
  });
}

const server = createServer(async (nodeReq, nodeRes) => {
  try {
    const url = new URL(nodeReq.url, `http://${nodeReq.headers.host}`);

    if (!url.pathname.startsWith("/api")) {
      let filePath = join(clientDir, url.pathname);
      if (existsSync(filePath) && statSync(filePath).isFile()) {
        const ext = extname(filePath);
        nodeRes.writeHead(200, { "Content-Type": MIME[ext] || "application/octet-stream" });
        const data = await new Promise((resolve, reject) =>
          readFile(filePath, (err, buf) => (err ? reject(err) : resolve(buf)))
        );
        nodeRes.end(data);
        return;
      }
    }

    const headers = {};
    for (const [k, v] of Object.entries(nodeReq.headers)) {
      if (v !== undefined) headers[k] = Array.isArray(v) ? v.join(", ") : v;
    }

    const init = { method: nodeReq.method, headers };
    if (["POST", "PUT", "PATCH"].includes(nodeReq.method)) {
      init.body = await readBody(nodeReq);
    }

    const webRes = await handler.fetch(new Request(url.toString(), init));
    const resHeaders = {};
    webRes.headers.forEach((v, k) => { resHeaders[k] = v; });
    nodeRes.writeHead(webRes.status, resHeaders);
    nodeRes.end(Buffer.from(await webRes.arrayBuffer()));
  } catch (err) {
    console.error("Server error:", err);
    nodeRes.writeHead(500, { "Content-Type": "text/plain" });
    nodeRes.end("Internal Server Error");
  }
});

const port = process.env.PORT || 3000;
server.listen(port, "0.0.0.0", () => {
  console.log(`Basma+ running at http://0.0.0.0:${port}`);
});
