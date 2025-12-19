"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";

type SearchResult = {
  product_id: string;
  score: number;
  metadata: {
    name?: string;
    keywords?: string[];
    image_urls?: string[];
    description?: string;
    [key: string]: unknown;
  };
};

const apiBase = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [topK, setTopK] = useState(5);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searchError, setSearchError] = useState<string | null>(null);

  async function handleSearch(e: FormEvent) {
    e.preventDefault();
    setSearchLoading(true);
    setSearchError(null);
    setSearchResults([]);

    try {
      const resp = await fetch(`${apiBase}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, top_k: topK }),
      });
      if (!resp.ok) {
        const detail = await resp.json().catch(() => ({}));
        throw new Error(detail.detail || "Search failed");
      }
      const data = await resp.json();
      setSearchResults(data.results as SearchResult[]);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Unknown error";
      setSearchError(msg);
    } finally {
      setSearchLoading(false);
    }
  }

  return (
    <main className="page">
      <header className="hero">
        <div>
          <p className="eyebrow">Semantic Search</p>
          <h1>Search Products</h1>
          <p className="lead">
            Search by keywords or natural language to find matching rugs and carpets.
            Results include similarity scores and product details.
          </p>
        </div>
        <nav className="nav-links">
          <Link href="/" className="nav-link">Home</Link>
          <Link href="/ingest" className="nav-link">Ingest</Link>
        </nav>
      </header>

      <section className="card">
        <div className="card-header">
          <div>
            <h2>Search Database</h2>
            <p className="muted">
              Enter a search query describing the rug you're looking for. 
              You can search by color, pattern, material, size, style, or any combination.
            </p>
          </div>
        </div>
        <form className="form" onSubmit={handleSearch}>
          <label className="field">
            <span>Search Query</span>
            <input
              required
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., navy blue Persian rug with geometric patterns, 8x10 wool hand-knotted"
            />
          </label>
          <label className="field-inline">
            <div>
              <span>Top K Results</span>
              <input
                type="number"
                min={1}
                max={20}
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                style={{ width: 80 }}
              />
            </div>
          </label>
          <button className="primary" type="submit" disabled={searchLoading}>
            {searchLoading ? "Searching..." : "Search"}
          </button>
          {searchError && <p className="error">{searchError}</p>}
        </form>

        {searchResults.length > 0 && (
          <div style={{ marginTop: "24px" }}>
            <h3 style={{ marginBottom: "16px" }}>
              Found {searchResults.length} result{searchResults.length !== 1 ? "s" : ""}
            </h3>
            <div className="grid">
              {searchResults.map((result) => (
                <article className="product" key={result.product_id}>
                  <header className="product-header">
                    <div>
                      <p className="eyebrow">
                        Score {(result.score * 100).toFixed(1)}%
                      </p>
                      <h3>{result.metadata.name || "Unnamed product"}</h3>
                    </div>
                    <code className="pill">{result.product_id}</code>
                  </header>
                  <p className="muted">
                    {result.metadata.description || "No description"}
                  </p>
                  {result.metadata.keywords && (
                    <div className="chips">
                      {(result.metadata.keywords as string[]).map((kw) => (
                        <span className="chip" key={kw}>
                          {kw}
                        </span>
                      ))}
                    </div>
                  )}
                  {result.metadata.image_urls && (
                    <div className="images">
                      {(result.metadata.image_urls as string[]).map((url) => (
                        <img key={url} src={url} alt="product" loading="lazy" />
                      ))}
                    </div>
                  )}
                </article>
              ))}
            </div>
          </div>
        )}

        {searchResults.length === 0 && !searchLoading && query && (
          <div style={{ marginTop: "24px", textAlign: "center", padding: "24px" }}>
            <p className="muted">No results found. Try a different search query.</p>
          </div>
        )}
      </section>
    </main>
  );
}

