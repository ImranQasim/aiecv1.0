import { initApiPassthrough } from "langgraph-nextjs-api-passthrough";

export const runtime = "nodejs";
export const maxDuration = 60;

type Handlers = ReturnType<typeof initApiPassthrough>;
type Method = "GET" | "POST" | "PUT" | "PATCH" | "DELETE" | "OPTIONS";

// Init on first request, not at import, so `next build` doesn't need the env vars.
let cached: Handlers | undefined;
function handlers(): Handlers {
  if (!cached) {
    cached = initApiPassthrough({
      apiUrl: process.env.LANGGRAPH_API_URL,
      apiKey: process.env.LANGSMITH_API_KEY,
      runtime: "nodejs",
    });
  }
  return cached;
}

// Render serves the backend Brotli-compressed. Node's fetch decompresses the
// body but the passthrough forwards the upstream `Content-Encoding: br` header,
// so the browser tries to decode already-plain bytes and fails with
// ERR_CONTENT_DECODING_FAILED. Drop the stale encoding/length headers.
function stripEncoding(res: Response): Response {
  const headers = new Headers(res.headers);
  headers.delete("content-encoding");
  headers.delete("content-length");
  return new Response(res.body, {
    status: res.status,
    statusText: res.statusText,
    headers,
  });
}

function route(method: Method) {
  return async (...args: unknown[]): Promise<Response> => {
    const handler = handlers()[method] as (
      ...a: unknown[]
    ) => Response | Promise<Response>;
    return stripEncoding(await handler(...args));
  };
}

export const GET = route("GET");
export const POST = route("POST");
export const PUT = route("PUT");
export const PATCH = route("PATCH");
export const DELETE = route("DELETE");
export const OPTIONS = route("OPTIONS");
