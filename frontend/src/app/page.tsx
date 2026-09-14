export default function HomePage() {
  return (
    <main className="container">
      <p className="eyebrow">ProofPocket / Project foundation</p>
      <h1>Your purchases. Your evidence. Your next step.</h1>
      <p className="intro">
        A home for receipts, warranties, and repair records—with answers grounded
        in your documents.
      </p>
      <section className="card" aria-labelledby="roadmap-heading">
        <h2 id="roadmap-heading">What we are building</h2>
        <ul>
          <li>Organize purchases and their supporting documents.</li>
          <li>Ask warranty questions and inspect the cited evidence.</li>
          <li>Track repairs and prepare support requests.</li>
        </ul>
        <p className="note">
          This is the initial scaffold. Uploads, accounts, and AI answers are not
          implemented yet.
        </p>
      </section>
    </main>
  );
}
