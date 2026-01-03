<template>
  <div class="details-view">
    <!-- Back -->
    <button class="back" @click="$router.back()">← Back to Results</button>

    <!-- Header -->
    <header class="header">
      <h1>SBC → NDLS</h1>
      <p class="date">Tue, 30 Dec</p>

      <div class="stats">
        <div class="stat">
          <span>Total Duration</span>
          <strong>4h 45m</strong>
        </div>
        <div class="stat">
          <span>Transfers</span>
          <strong>1</strong>
        </div>
        <div class="stat">
          <span>Journey Type</span>
          <strong>Balanced Route</strong>
        </div>
      </div>
    </header>

    <!-- Timeline -->
    <section class="card">
      <h2>Journey Timeline</h2>

      <div class="timeline">
        <div class="stop">
          <div class="dot"></div>
          <div>
            <h3>SBC</h3>
            <p class="train">🚆 12627 — Karnataka Express</p>
            <p>Departs: <strong>11:00</strong> · Arrives: <strong>12:55</strong></p>
          </div>
        </div>

        <div class="transfer">
          ⏳ Wait at station: <strong>40 min</strong>
        </div>

        <div class="stop">
          <div class="dot"></div>
          <div>
            <h3>NDLS</h3>
            <p class="train">🚆 12007 — Jan Shatabdi</p>
            <p>Departs: <strong>13:35</strong> · Arrives: <strong>14:45</strong></p>
          </div>
        </div>
      </div>
    </section>

    <!-- Coach -->
    <section class="card">
      <h2>Coach Layout (Indicative)</h2>
      <div class="coach">
        <span class="engine">Engine</span>
        <span>C1</span>
        <span>C2</span>
        <span>C3</span>
        <span>C4</span>
      </div>
      <p class="hint">Coach position is indicative and may vary.</p>
    </section>
  </div>
</template>

<script setup>
/* No JS animation libraries needed */
</script>

<style scoped>
.details-view {
  max-width: 900px;
  margin: auto;
  padding: 2.5rem 1.5rem;
  font-family: system-ui, -apple-system, BlinkMacSystemFont,
    "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* ---------- Back ---------- */
.back {
  background: none;
  border: none;
  color: #0066cc;
  cursor: pointer;
  font-size: 0.95rem;
  margin-bottom: 1rem;
  transition: opacity 0.2s ease;
}
.back:hover {
  opacity: 0.7;
}

/* ---------- Header ---------- */
.header h1 {
  font-size: 2.2rem;
  margin-bottom: 0.3rem;
  animation: fadeUp 0.6s ease forwards;
}

.date {
  color: #666;
  margin-bottom: 1.5rem;
  animation: fadeUp 0.6s ease forwards;
  animation-delay: 0.1s;
}

.stats {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.stat {
  background: #f5f9ff;
  padding: 0.8rem 1rem;
  border-radius: 10px;
  min-width: 160px;
  opacity: 0;
  animation: fadeUp 0.6s ease forwards;
}

.stat:nth-child(1) { animation-delay: 0.15s; }
.stat:nth-child(2) { animation-delay: 0.25s; }
.stat:nth-child(3) { animation-delay: 0.35s; }

.stat span {
  font-size: 0.75rem;
  color: #555;
}

.stat strong {
  font-size: 1.1rem;
}

/* ---------- Cards ---------- */
.card {
  background: white;
  border-radius: 14px;
  padding: 1.5rem;
  margin-top: 2rem;
  box-shadow: 0 10px 30px rgba(0,0,0,0.08);
  opacity: 0;
  animation: fadeUp 0.7s ease forwards;
}

.card h2 {
  margin-bottom: 1.2rem;
}

/* ---------- Timeline ---------- */
.timeline {
  position: relative;
  padding-left: 2rem;
}

.timeline::before {
  content: "";
  position: absolute;
  left: 8px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #0066cc;
}

.stop {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.6rem;
  opacity: 0;
  animation: fadeUp 0.6s ease forwards;
}

.stop:nth-of-type(1) { animation-delay: 0.3s; }
.stop:nth-of-type(2) { animation-delay: 0.55s; }

.dot {
  width: 16px;
  height: 16px;
  background: #0066cc;
  border-radius: 50%;
  margin-left: -2px;
}

.train {
  font-weight: 500;
}

.transfer {
  margin: 0 0 1.5rem 1.2rem;
  color: #666;
  font-size: 0.9rem;
  opacity: 0;
  animation: fadeUp 0.6s ease forwards;
  animation-delay: 0.45s;
}

/* ---------- Coach ---------- */
.coach {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.coach span {
  background: #f2f2f2;
  padding: 0.6rem 0.9rem;
  border-radius: 8px;
  font-weight: 500;
  opacity: 0;
  animation: fadeUp 0.5s ease forwards;
}

.coach span:nth-child(1) { animation-delay: 0.2s; }
.coach span:nth-child(2) { animation-delay: 0.3s; }
.coach span:nth-child(3) { animation-delay: 0.4s; }
.coach span:nth-child(4) { animation-delay: 0.5s; }
.coach span:nth-child(5) { animation-delay: 0.6s; }

.engine {
  background: #0066cc;
  color: white;
}

.hint {
  margin-top: 0.6rem;
  font-size: 0.85rem;
  color: #666;
  opacity: 0;
  animation: fadeUp 0.5s ease forwards;
  animation-delay: 0.7s;
}

/* ---------- Animations ---------- */
@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(14px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ---------- Responsive ---------- */
@media (max-width: 600px) {
  .stats {
    flex-direction: column;
  }
  .header h1 {
    font-size: 1.8rem;
  }
}
</style>
