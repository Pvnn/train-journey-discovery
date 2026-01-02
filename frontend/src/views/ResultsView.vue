<template>
  <div class="results-view">
    <!-- Search Summary -->
    <header class="summary">
      <h2>
        Journeys from {{ origin }} to {{ destination }}
      </h2>
      <p>On {{ date }}</p>
    </header>

    <!-- Filters (UI only) -->
    <section class="filters">
      <select>
        <option>Sort by</option>
        <option>Fastest</option>
        <option>Cheapest</option>
        <option>Least transfers</option>
      </select>

      <select>
        <option>Train Class</option>
        <option>AC</option>
        <option>Sleeper</option>
        <option>General</option>
      </select>
    </section>

    <!-- Loading State -->
    <section v-if="loading" class="loading">
      <div class="skeleton" v-for="n in 3" :key="n"></div>
    </section>

    <!-- Empty State -->
    <section v-else-if="journeys.length === 0" class="empty">
      No journeys found. Try different dates or stations.
    </section>

    <!-- Results -->
    <section v-else class="results">
      <JourneyCard
        v-for="journey in journeys"
        :key="journey.trainNumber"
        v-bind="journey"
      />
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import JourneyCard from "../components/JourneyCard.vue";

/* mock search summary */
const origin = "SBC";
const destination = "NDLS";
const date = "30 Dec";

/* state */
const loading = ref(true);
const journeys = ref([]);

/* mock data */
onMounted(() => {
  setTimeout(() => {
    journeys.value = [
      {
        trainNumber: "12627",
        trainName: "Karnataka Express",
        departureStation: "SBC",
        departureTime: "11:00",
        arrivalStation: "NDLS",
        arrivalTime: "12:55",
        duration: "4h 45m",
        transfers: 1,
        fare: 850,
        trainClass: "AC",
        comfortScore: 4,
      },
      {
        trainNumber: "12007",
        trainName: "Jan Shatabdi",
        departureStation: "SBC",
        departureTime: "13:35",
        arrivalStation: "NDLS",
        arrivalTime: "14:45",
        duration: "5h 10m",
        transfers: 0,
        fare: 620,
        trainClass: "Sleeper",
        comfortScore: 3,
      },
    ];

    loading.value = false;
  }, 1200);
});
</script>

<style scoped>
.results-view {
  max-width: 900px;
  margin: auto;
  padding: 1.5rem;
}

/* Summary */
.summary {
  margin-bottom: 1rem;
}

.summary h2 {
  color: #0066cc;
}

/* Filters */
.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

select {
  padding: 0.4rem;
}

/* Skeleton loading */
.loading .skeleton {
  height: 110px;
  background: linear-gradient(
    90deg,
    #eee 25%,
    #ddd 37%,
    #eee 63%
  );
  background-size: 400% 100%;
  animation: shimmer 1.2s infinite;
  border-radius: 12px;
  margin-bottom: 1rem;
}

@keyframes shimmer {
  0% {
    background-position: 100% 0;
  }
  100% {
    background-position: -100% 0;
  }
}

/* Empty */
.empty {
  text-align: center;
  color: #777;
  margin-top: 2rem;
}
</style>
