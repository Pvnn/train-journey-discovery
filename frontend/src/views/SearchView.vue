<template>
  <section class="hero">
    <!-- Base dark overlay -->
    <div class="overlay"></div>

    <!-- Animated gradient overlay -->
    <div class="gradient-animation"></div>

    <div class="content">
      <div class="text">
        <h1>Beyond Direct Trains</h1>
        <p>
          Find smart multi-hop train journeys across India —
          when direct trains don’t exist.
        </p>
      </div>

      <div class="search-card">
        <SearchForm />
      </div>
    </div>
  </section>
</template>

<script setup>
import SearchForm from "../components/SearchForm.vue";
</script>

<style scoped>
/* ===============================
   HERO BASE
================================ */
.hero {
  position: relative;
  min-height: 85vh;
  background-image: url("../assets/train-hero.jpg");
  background-size: cover;
  background-position: center;
  overflow: hidden;
  display: flex;
  align-items: center;

  font-family: system-ui, -apple-system, BlinkMacSystemFont,
    "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* ===============================
   DARK OVERLAY
================================ */
.overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  z-index: 1;
}

/* ===============================
   ANIMATED GRADIENT OVERLAY
================================ */
.gradient-animation {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    120deg,
    rgba(0, 102, 204, 0.25),
    rgba(255, 153, 51, 0.18),
    rgba(0, 102, 204, 0.25)
  );
  background-size: 300% 300%;
  animation: gradientMove 18s ease infinite;
  z-index: 2;
}

@keyframes gradientMove {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* ===============================
   CONTENT
================================ */
.content {
  position: relative;
  z-index: 3;
  max-width: 1200px;
  margin: auto;
  padding: 2.5rem;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3.5rem;
  align-items: center;
}

/* ===============================
   TEXT
================================ */
.text h1 {
  font-size: 3rem;
  font-weight: 800;
  letter-spacing: -0.6px;
  color: #ffffff;
  margin-bottom: 1rem;
}

.text p {
  font-size: 1.15rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.95);
  line-height: 1.7;
  max-width: 500px;
}

/* ===============================
   SEARCH CARD
================================ */
.search-card {
  background: white;
  border-radius: 18px;
  padding: 2rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.35);
}

/* ==================================================
   🔥 SEARCH FORM TYPOGRAPHY FIX (THIS IS THE KEY)
   Applies ONLY to City / To / Date / Time / Button
================================================== */

/* Input text */
.search-card :deep(input) {
  font-size: 1.05rem;
  font-weight: 500;
  color: #111827;
}

/* Placeholder text */
.search-card :deep(input::placeholder) {
  font-weight: 400;
  color: #6b7280;
}

/* Labels like From / To / Date */
.search-card :deep(label) {
  font-size: 0.85rem;
  font-weight: 600;
  color: #374151;
  letter-spacing: 0.02em;
}

/* Button text */
.search-card :deep(button) {
  font-size: 1rem;
  font-weight: 600;
  letter-spacing: 0.3px;
}

/* ===============================
   RESPONSIVE
================================ */
@media (max-width: 900px) {
  .content {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .text p {
    margin: auto;
  }
}

@media (max-width: 600px) {
  .text h1 {
    font-size: 2.2rem;
  }

  .text p {
    font-size: 1rem;
  }

  .search-card {
    padding: 1.5rem;
  }
}
</style>
