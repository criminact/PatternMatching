"use client";

import Link from "next/link";

export default function HomePage() {
  return (
    <main className="page">
      <header className="hero">
        <div>
          <p className="eyebrow">Gemini + Chroma + Next.js</p>
          <h1>Semantic Product Retrieval</h1>
          <p className="lead">
            Upload product image URLs and keywords, let Gemini write the
            description, and search semantically to find the best matches.
          </p>
        </div>
      </header>

      <div className="grid" style={{ marginTop: "32px", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))" }}>
        <Link href="/ingest" className="card" style={{ textDecoration: "none", display: "block" }}>
          <div className="card-header">
            <div>
              <p className="eyebrow">Step 1</p>
              <h2>Ingest Product</h2>
              <p className="muted">
                Add new products to the database. Upload images, provide keywords, 
                and let Gemini generate detailed visual descriptions.
              </p>
            </div>
          </div>
          <div style={{ marginTop: "16px" }}>
            <button className="primary" style={{ width: "100%" }}>
              Go to Ingest Page →
            </button>
          </div>
        </Link>

        <Link href="/search" className="card" style={{ textDecoration: "none", display: "block" }}>
          <div className="card-header">
            <div>
              <p className="eyebrow">Step 2</p>
              <h2>Search Products</h2>
              <p className="muted">
                Search the database using natural language or keywords. 
                Find rugs and carpets that match your description.
              </p>
            </div>
          </div>
          <div style={{ marginTop: "16px" }}>
            <button className="primary" style={{ width: "100%" }}>
              Go to Search Page →
            </button>
          </div>
        </Link>
      </div>
    </main>
  );
}
