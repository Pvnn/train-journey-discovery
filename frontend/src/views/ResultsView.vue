<template>
  <div class="results-view">
    <!-- Summary -->
    <header class="summary">
      <h2>Journeys from {{ origin }} to {{ destination }}</h2>
      <p>On {{ date }}</p>
      <p class="count">{{ filteredAndSortedJourneys.length }} results</p>
    </header>

    <!-- Filters -->
    <section class="filters">
      <select v-model="sortBy">
        <option value="">Sort by</option>
        <option value="fastest">Fastest</option>
        <option value="cheapest">Cheapest</option>
        <option value="transfers">Least transfers</option>
        <option value="comfort">Best comfort</option>
      </select>

      <select v-model="maxTransfers">
        <option value="">Max transfers</option>
        <option value="0">Direct only</option>
        <option value="1">Up to 1</option>
        <option value="2">Up to 2</option>
      </select>

      <label>
        <input type="checkbox" value="AC" v-model="selectedClasses" /> AC
      </label>
      <label>
        <input type="checkbox" value="Sleeper" v-model="selectedClasses" />
        Sleeper
      </label>
      <label>
        <input type="checkbox" value="General" v-model="selectedClasses" />
        General
      </label>

      <button class="clear" @click="clearFilters">Clear Filters</button>
    </section>

    <!-- Results -->
    <TransitionGroup name="fade-up" tag="section" class="results">
      <JourneyCard
        v-for="journey in filteredAndSortedJourneys"
        :key="journey.trainNumber"
        v-bind="journey"
      />
    </TransitionGroup>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import JourneyCard from "../components/JourneyCard.vue";

/* Mock summary */
const origin = "haripad";
const destination = "aluva";
const date = "2026-11-01";

/* Filters */
const sortBy = ref("");
const maxTransfers = ref("");
const selectedClasses = ref([]);

/* Mock data */
const journeys = ref([
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
]);

/* Filter + sort logic */
const filteredAndSortedJourneys = computed(() => {
  let list = [...journeys.value];

  if (maxTransfers.value !== "") {
    list = list.filter(
      (j) => j.transfers <= Number(maxTransfers.value)
    );
  }

  if (selectedClasses.value.length) {
    list = list.filter((j) =>
      selectedClasses.value.includes(j.trainClass)
    );
  }

  if (sortBy.value === "cheapest") {
    list.sort((a, b) => a.fare - b.fare);
  } else if (sortBy.value === "transfers") {
    list.sort((a, b) => a.transfers - b.transfers);
  } else if (sortBy.value === "comfort") {
    list.sort((a, b) => b.comfortScore - a.comfortScore);
  }

  return list;
});

const clearFilters = () => {
  sortBy.value = "";
  maxTransfers.value = "";
  selectedClasses.value = [];
};
</script>

<style scoped>
.results-view {
  max-width: 960px;
  margin: auto;
  padding: 2rem;
}

/* Summary */
.summary h2 {
  color: #0066cc;
}

.count {
  color: #666;
  margin-top: 0.3rem;
}

/* Filters */
.filters {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin: 1.5rem 0;
}

select {
  padding: 0.4rem;
}

.clear {
  background: #f2f2f2;
  border: none;
  padding: 0.4rem 0.8rem;
  cursor: pointer;
}

/* Results container */
.results {
  margin-top: 1.5rem;
}

/* ===============================
   FADE-UP STAGGER ANIMATION
================================ */
.fade-up-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.fade-up-enter-active {
  transition: all 0.4s ease;
}

.fade-up-enter-to {
  opacity: 1;
  transform: translateY(0);
}
</style>
