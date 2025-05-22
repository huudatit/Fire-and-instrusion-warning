<template>
  <div class="container">
    <div class="cards">
      <SensorCard
        title="Phát hiện lửa"
        :value="fireDetected ? 'Có lửa' : 'Bình thường'"
        :warning="fireDetected"
        :warning-message="
          fireDetected ? 'Cảnh báo: Có cháy!' : 'Không có nguy cơ'
        "
      />

      <SensorCard
        title="Xâm nhập mạng"
        :value="intrusionType"
        :warning="intrusionType !== 'Bình thường'"
        :warning-message="
          intrusionType !== 'Bình thường'
            ? 'Cảnh báo: ' + intrusionType
            : 'Mạng an toàn'
        "
      />

      <SensorCard
        title="Nhiệt độ"
        :value="temperature + ' °C'"
        :warning="temperature > 50 || temperature < 20"
        :warning-message="
          temperature > 50 ? 'Cảnh báo: Nhiệt độ cao!' :
          temperature < 20 ? 'Cảnh báo: Nhiệt độ thấp!' :
          'Nhiệt độ bình thường'
      "
      />

      <SensorCard
        title="Độ ẩm"
        :value="humidity + ' %'"
        :warning="humidity > 80 || humidity < 30"
        :warning-message="
          humidity > 80 ? 'Cảnh báo: Độ ẩm cao!' :
          humidity < 30 ? 'Cảnh báo: Độ ẩm thấp!' :
          'Độ ẩm bình thường'
      "
      />
      <div style="display: flex; justify-content: center; gap: 20px; margin-top: 20px;">
      <button @click="clearLogs" style="padding: 10px 20px; background-color: red; color: white; border: none; border-radius: 5px; cursor: pointer;">
        Xoá nhật ký
      </button>
      <button @click="sendEmailNow" style="padding: 10px 20px; background-color: green; color: white; border: none; border-radius: 5px;">
        Gửi tin nhắn về gmail
      </button>
    </div>
    </div>
    <h2 style="margin-top: 40px;">Nhật ký hệ thống</h2>
    <table style="margin: auto; border-collapse: collapse;">
    <thead>
    <tr>
      <th style="border: 1px solid #ccc; padding: 8px;">Thời gian</th>
      <th style="border: 1px solid #ccc; padding: 8px;">Sự kiện</th>
    </tr>
  </thead>
  <tbody>
    <tr v-for="log in logs" :key="log.timestamp">
      <td style="border: 1px solid #ccc; padding: 8px;">{{ log.timestamp }}</td>
      <td style="border: 1px solid #ccc; padding: 8px;">
         {{ log.fire ? 'Có lửa' : 'Không' }},
         {{ log.intrusion }},
         {{ log.temperature }} °C,
         {{ log.humidity }} %
      </td>
    </tr>
  </tbody>
</table>

  </div>
</template>

<script>
import SensorCard from "../components/SensorCard.vue";

export default {
  components: { SensorCard },
  data() {
    return {
      fireDetected: false,
      intrusionType: "Bình thường",
      temperature: 30.0,
      humidity: 50.0,
      logs: []
    };
  },
  mounted() {
    this.fetchStatus();
    this.fetchLogs();
    this.setUserEmail();
    setInterval(this.fetchStatus, 2000); // gọi lại mỗi 3s
    setInterval(this.fetchLogs, 5000);
  },
  methods: {
    async fetchStatus() {
      try {
        const response = await fetch("http://localhost:5000/api/status");
        const data = await response.json();
        this.fireDetected = data.fire;
        this.intrusionType = data.intrusion;
        this.temperature = data.temperature;
        this.humidity = data.humidity;

        //this.sendStatusToBackend();
      } catch (error) {
        console.error("Không lấy được trạng thái từ server:", error);
      }
    },
    async fetchLogs() {
      try {
      const response = await fetch("http://localhost:5000/api/logs");
      const data = await response.json();
      const allLogs = data.logs;
      this.logs = allLogs.slice(-5).reverse();
      } catch (error) {
      console.error("Không lấy được log từ server:", error);
      }
    },
    async clearLogs() {
    if (confirm("Bạn có chắc chắn muốn xoá toàn bộ nhật ký?")) {
      try {
      const response = await fetch("http://localhost:5000/api/clear_logs", {
        method: "POST"
      });
      const result = await response.json();
      console.log(result.message);
      this.logs = []; // cập nhật giao diện
      } catch (error) {
      console.error("Lỗi khi xoá log:", error);
      }
    }
    },
    async sendStatusToBackend() {
    const email = localStorage.getItem("userEmail"); 
    const payload = {
      fire: this.fireDetected,
      intrusion: this.intrusionType,
      temperature: this.temperature,
      humidity: this.humidity,
      email: email  
    };
    try {
      await fetch("http://localhost:5000/api/set_status", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
    } catch (error) {
      console.error("Không gửi được dữ liệu:", error);
    }
  },
    async sendEmailNow() {
    try {
      const res = await fetch("http://localhost:5000/api/send_email_now", {
        method: "POST"
      });
      const result = await res.json();
      alert(result.message); // Hiển thị kết quả cho người dùng
    } catch (error) {
      console.error("Lỗi khi gửi email thủ công:", error);
      alert("Không thể gửi email. Vui lòng thử lại.");
    }
  },
  async setUserEmail() {
    const email = localStorage.getItem("userEmail");
    if (!email) {
      console.warn("Chưa có email trong localStorage");
      return;
    }
    try {
      const res = await fetch("http://localhost:5000/api/set_email", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email })
      });
      const result = await res.json();
      console.log("Email đã gửi đến server:", result);
    } catch (err) {
      console.error("Không thể gửi email lên server:", err);
    }
  },
  },
};
</script>


<style>
.container {
  padding: 20px;
  font-family: Arial, sans-serif;
  text-align: center;
}
.cards {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 20px;
  margin-top: 30px;
}
.log-section {
  margin-top: 40px;
  text-align: center;
}

.log-table {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  border-collapse: collapse;
}

.log-table th,
.log-table td {
  border: 1px solid #ccc;
  padding: 10px;
}

.log-table th {
  background-color: #f0f0f0;
  font-weight: bold;
}

</style>

