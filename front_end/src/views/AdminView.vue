<template>
    <div class="admin-container">
      <h2> Admin – Giả lập dữ liệu mạng</h2>
      <div class="btn-group">
        <button @click="simulate('normal')">Giả lập Bình thường</button>
        <button @click="simulate('attack')">Giả lập Tấn công</button>
      </div>
      <p v-if="result"> Kết quả từ server: <strong>{{ result }}</strong></p>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  
  export default {
    data() {
      return {
        result: "",
      };
    },
    methods: {
      simulate(type) {
        const normal_input = {
          protocol_type: 0,
          flag: 1,
          src_bytes: 300,
          dst_bytes: 1000,
          count: 2,
          same_srv_rate: 0.8,
          diff_srv_rate: 0.1,
          dst_host_srv_count: 100,
          dst_host_same_srv_rate: 0.9,
          dst_host_same_src_port_rate: 0.8,
        };
  
        const attack_input = {
          protocol_type: 1,
          flag: 3,
          src_bytes: 0,
          dst_bytes: 2000,
          count: 100,
          same_srv_rate: 0.1,
          diff_srv_rate: 0.9,
          dst_host_srv_count: 255,
          dst_host_same_srv_rate: 0.02,
          dst_host_same_src_port_rate: 0.01,
        };
  
        const infer_data = type === "normal" ? normal_input : attack_input;
  
        axios
          .post("https://fire-and-instrusion-warning.onrender.com/api/infer", infer_data)
          .then((res) => {
            const label = res.data.intrusion;
            this.result = label;

      // 2. Sau khi có kết quả → gửi về /api/set_status để dashboard cập nhật
          axios
              .post("https://fire-and-instrusion-warning.onrender.com/api/set_status", {
                fire: false,
                intrusion: label,
                temperature: 30.0,
                humidity: 50.0,
              })
              .then(() => {
                console.log("Đã cập nhật trạng thái vào dashboard");
              })
              .catch((err) => {
                console.error("Lỗi khi cập nhật /api/set_status", err);
              });
          })
        .catch((err) => {
          this.result = "Lỗi gửi yêu cầu!";
          console.error(err);
        });
      },
    },
  };
  </script>
  
  <style scoped>
  .admin-container {
    text-align: center;
    padding: 30px;
  }
  
  .btn-group button {
    padding: 12px 20px;
    margin: 10px;
    font-size: 16px;
    border-radius: 8px;
    border: none;
    background-color: #007bff;
    color: white;
    cursor: pointer;
  }
  
  .btn-group button:hover {
    background-color: #0056b3;
  }
  </style>
  