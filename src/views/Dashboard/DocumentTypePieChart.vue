<script setup>
import { ref, onMounted } from "vue"
import { Chart, registerables } from "chart.js"
import api from "@/api"

Chart.register(...registerables)

const canvasRef = ref(null)

async function loadChart() {

  const res = await api.get("/dashboard/document-type-distribution")

  const labels = res.data.map(i => i.type)
  const data = res.data.map(i => i.count)

  new Chart(canvasRef.value, {
    type: "pie",
    data: {
      labels,
        datasets: [
        {
            data,
            backgroundColor: [
            "#22c55e",   // Public → green
            "#f59e0b",   // Restricted → yellow
            "#ef4444"    // Confidential → red
            ]
        }
        ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: "bottom"
        }
      }
    }
  })
}

onMounted(loadChart)
</script>

<template>
  <div class="bg-white p-6 rounded shadow">
    <div class="text-sm text-gray-500 mb-3">
      Document Type Distribution
    </div>
    <canvas ref="canvasRef"></canvas>
  </div>
</template>