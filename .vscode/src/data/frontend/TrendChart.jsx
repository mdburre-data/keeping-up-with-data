import React, { useState } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  TimeScale,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import "chartjs-adapter-date-fns";

ChartJS.register(
  LineElement,
  PointElement,
  LinearScale,
  TimeScale,
  Title,
  Tooltip,
  Legend
);

export default function TrendChart() {
  const [kw, setKw] = useState("oversized blazer");
  const [chartData, setChartData] = useState(null);

  async function fetchPredictions() {
    const res = await fetch(
      `http://127.0.0.1:8000/predict?keyword=${encodeURIComponent(kw)}&periods=12`
    );
    const json = await res.json();

    // Format data for chart
    const labels = json.predictions.map((p) => p.ds);
    const values = json.predictions.map((p) => p.yhat);

    setChartData({
      labels,
      datasets: [
        {
          label: `Predicted search trend for "${json.keyword}"`,
          data: values,
          borderColor: "rgba(75,192,192,1)",
          backgroundColor: "rgba(75,192,192,0.2)",
          tension: 0.3,
        },
      ],
    });
  }

  return (
    <div style={{ maxWidth: "700px", margin: "auto", padding: "20px" }}>
      <h2 className="text-xl font-bold mb-2">Fashion Trend Predictor</h2>

      <input
        value={kw}
        onChange={(e) => setKw(e.target.value)}
        placeholder="Enter keyword..."
        className="border px-2 py-1 mr-2 rounded"
      />
      <button
        onClick={fetchPredictions}
        className="bg-blue-500 text-white px-3 py-1 rounded"
      >
        Predict
      </button>

      {chartData && (
        <div style={{ marginTop: "20px" }}>
          <Line
            data={chartData}
            options={{
              responsive: true,
              scales: {
                x: {
                  type: "time",
                  time: {
                    unit: "week",
                  },
                },
                y: {
                  beginAtZero: true,
                },
              },
            }}
          />
        </div>
      )}
    </div>
  );
}
