"use client";

import { FormEvent, useMemo, useState } from "react";
import Link from "next/link";

type IngestResponse = {
  product_id: string;
  description: string;
  metadata: Record<string, unknown>;
};

const apiBase = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

function parseList(input: string): string[] {
  return input
    .split(/\r?\n|,/)
    .map((item) => item.trim())
    .filter(Boolean);
}

export default function IngestPage() {
  const [name, setName] = useState("");
  const [keywordsInput, setKeywordsInput] = useState("");
  const [imageUrlsInput, setImageUrlsInput] = useState("");
  const [description, setDescription] = useState("");
  const [descLoading, setDescLoading] = useState(false);
  const [descError, setDescError] = useState<string | null>(null);
  const [ingestLoading, setIngestLoading] = useState(false);
  const [ingestResult, setIngestResult] = useState<IngestResponse | null>(
    null
  );
  const [ingestError, setIngestError] = useState<string | null>(null);

  const keywordList = useMemo(() => parseList(keywordsInput), [keywordsInput]);
  const imageUrlList = useMemo(
    () => parseList(imageUrlsInput),
    [imageUrlsInput]
  );
  const ingestReady =
    !!name.trim() &&
    keywordList.length > 0 &&
    imageUrlList.length > 0 &&
    !!description.trim();

  async function handleIngest(e: FormEvent) {
    e.preventDefault();
    if (!ingestReady) {
      setIngestError(
        "Provide name, keywords, image URLs, and generate a description first."
      );
      return;
    }
    setIngestLoading(true);
    setIngestError(null);
    setIngestResult(null);

    try {
      const resp = await fetch(`${apiBase}/ingest`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          keywords: keywordList,
          image_urls: imageUrlList,
          description: description.trim(),
        }),
      });
      if (!resp.ok) {
        const errorData = await resp.json().catch(() => ({}));
        const errorMsg = errorData.detail || errorData.message || "Ingestion failed";
        if (Array.isArray(errorData.errors)) {
          const formattedErrors = errorData.errors.map((e: any) => {
            const field = e.loc?.join(" -> ") || "unknown";
            return `${field}: ${e.msg}`;
          }).join("; ");
          throw new Error(formattedErrors || errorMsg);
        }
        throw new Error(errorMsg);
      }
      const data = (await resp.json()) as IngestResponse;
      setIngestResult(data);
      // Reset form on success
      setName("");
      setKeywordsInput("");
      setImageUrlsInput("");
      setDescription("");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Unknown error";
      setIngestError(msg);
    } finally {
      setIngestLoading(false);
    }
  }

  async function handleGenerateDescription(e: FormEvent) {
    e.preventDefault();
    if (description.trim()) {
      return;
    }
    setDescLoading(true);
    setDescError(null);
    try {
      const resp = await fetch(`${apiBase}/generate_description`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          keywords: keywordList,
          image_urls: imageUrlList,
        }),
      });
      if (!resp.ok) {
        const detail = await resp.json().catch(() => ({}));
        throw new Error(detail.detail || "Generation failed");
      }
      const data = await resp.json();
      setDescription(data.description || "");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Unknown error";
      setDescError(msg);
    } finally {
      setDescLoading(false);
    }
  }

  return (
    <main className="page">
      <header className="hero">
        <div>
          <p className="eyebrow">Gemini + Chroma + Next.js</p>
          <h1>Ingest Product</h1>
          <p className="lead">
            Upload product image URLs and keywords, let Gemini write the
            description, and store it in the semantic search database.
          </p>
        </div>
        <nav className="nav-links">
          <Link href="/" className="nav-link">Home</Link>
          <Link href="/search" className="nav-link">Search</Link>
        </nav>
      </header>

      <section className="card">
        <div className="card-header">
          <div>
            <h2>Add New Product</h2>
            <p className="muted">
              Provide name, keywords, and image URLs. Generate a description with Gemini (required), then you can edit it before ingesting.
            </p>
          </div>
        </div>
        <form className="form" onSubmit={handleIngest}>
          <label className="field">
            <span>Name</span>
            <input
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Rug"
            />
          </label>
          <label className="field">
            <span>Keywords (comma or newline separated)</span>
            <textarea
              required
              value={keywordsInput}
              onChange={(e) => setKeywordsInput(e.target.value)}
              placeholder="hand-knotted, wool, 8x10, Persian, low-pile, navy/ivory, geometric"
              rows={2}
            />
            <small>{keywordList.length} keywords</small>
          </label>
          <label className="field">
            <span>Image URLs (comma or newline separated)</span>
            <textarea
              required
              value={imageUrlsInput}
              onChange={(e) => setImageUrlsInput(e.target.value)}
              placeholder="https://..."
              rows={3}
            />
            <small>{imageUrlList.length} images</small>
          </label>
          <label className="field">
            <span>Description (generated by Gemini)</span>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Generate a rug/carpet description with Gemini"
              rows={5}
            />
            <div className="actions-row">
              <button
                type="button"
                className="secondary"
                onClick={handleGenerateDescription}
                disabled={descLoading || keywordList.length === 0 || imageUrlList.length === 0 || !name || !!description.trim()}
              >
                {descLoading ? "Generating..." : "Generate with Gemini"}
              </button>
              <small className="muted">
                Required: generate with Gemini before ingesting. You can edit the description after generation.
              </small>
            </div>
            {descError && <p className="error">{descError}</p>}
          </label>
          <button className="primary" type="submit" disabled={ingestLoading || !ingestReady}>
            {ingestLoading ? "Ingesting..." : "Ingest Product"}
          </button>
          {!ingestReady && (
            <p className="muted small">
              Ingest requires name, keywords, image URLs, and a generated description.
            </p>
          )}
          {ingestError && <p className="error">{ingestError}</p>}
          {ingestResult && (
            <div className="result">
              <p className="eyebrow">Successfully Stored</p>
              <p>
                Product ID: <code>{ingestResult.product_id}</code>
              </p>
              <p className="muted">{ingestResult.description}</p>
            </div>
          )}
        </form>
      </section>
    </main>
  );
}

