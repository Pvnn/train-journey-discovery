<template>
  <div class="search-view">
    <!-- Hero -->
    <header class="hero">
      <h1>Multi-Hop Train Journey Planner</h1>
      <p>Discover train routes beyond direct connections</p>
    </header>

    <!-- Search Form -->
    <SearchForm @search="handleSearch" />

    <!-- Results -->
    <section v-if="searched" class="results">
      <h2>Search Results</h2>

      <JourneyCard
        v-for="journey in journeys"
        :key="journey.trainNumber"
        v-bind="journey"
        @view-details="handleViewDetails"
      />
    </section>
  </div>
</template>

<script setup>
import { ref } from "vue";
import SearchForm from "../components/SearchForm.vue";
import JourneyCard from "../components/JourneyCard.vue";

const searched = ref(false);
const journeys = ref([]);

const handleSearch = (params) => {
  console.log("Search params:", params);

  searched.value = true;

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
      transfers: 1,
      fare: 620,
      trainClass: "Sleeper",
      comfortScore: 3,
    },
  ];
};

const handleViewDetails = (payload) => {
  console.log("View details clicked for:", payload.trainNumber);
};
</script>

<style scoped>
.search-view {
  max-width: 900px;
  margin: auto;
  padding: 1.5rem;
}

.hero {
  text-align: center;
  margin-bottom: 2rem;
}

.hero h1 {
  color: #0066cc;
}

.hero p {
  color: #555;
}

.results {
  margin-top: 2rem;
}
</style>
