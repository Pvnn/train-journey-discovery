import { createRouter, createWebHistory } from "vue-router";

import SearchView from "../views/SearchView.vue";
import ResultsView from "../views/ResultsView.vue";
import JourneyDetailsView from "../views/JourneyDetailsView.vue";

const routes = [
  {
    path: "/",
    name: "search",
    component: SearchView,
  },
  {
    path: "/results",
    name: "results",
    component: ResultsView,
  },
  {
    path: "/journey/:id",
    name: "journey-details",
    component: JourneyDetailsView,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
