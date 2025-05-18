<template>
  <div class="admin-dashboard">
    <h1 class="page-title">Bảng điều khiển Admin</h1>
    
    <!-- Thanh điều hướng -->
    <div class="tab-navigation">
      <button 
        v-for="tab in tabs" 
        :key="tab.id" 
        @click="activeTab = tab.id"
        :class="['tab-btn', { active: activeTab === tab.id }]"
      >
        {{ tab.name }}
      </button>
    </div>
    
    <!-- Tổng quan -->
    <div v-if="activeTab === 'dashboard'" class="panel">
      <h2>Tổng quan</h2>
      <div class="stats-summary">
        <div class="stat-item">
          <strong>Tổng người dùng:</strong> {{ users.length }}
        </div>
        <div class="stat-item">
          <strong>Cảnh báo chưa xử lý:</strong> {{ unhandledAlerts.length }}
        </div>
        <div class="stat-item">
          <strong>Người dùng mới (7 ngày):</strong> {{ newUsers }}
        </div>
        <div class="stat-item">
          <strong>Cảnh báo hôm nay:</strong> {{ todayAlerts }}
        </div>
      </div>
    </div>
    
    <!-- Quản lý người dùng -->
    <div v-if="activeTab === 'users'" class="panel">
      <h2>Quản lý người dùng</h2>
      <div class="search-bar">
        <input 
          type="text" 
          v-model="userSearchQuery" 
          placeholder="Tìm kiếm người dùng..." 
          @input="searchUsers"
        />
      </div>
      
      <div v-if="isLoadingUsers" class="loading">Đang tải...</div>
      
      <table v-else-if="filteredUsers.length" class="data-table">
        <thead>
          <tr>
            <th @click="sortUsers('name')">Tên</th>
            <th @click="sortUsers('email')">Email</th>
            <th @click="sortUsers('createdAt')">Ngày đăng ký</th>
            <th>Trạng thái</th>
            <th>Thao tác</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in filteredUsers" :key="user.id">
            <td>{{ user.name || 'Chưa cập nhật' }}</td>
            <td>{{ user.email }}</td>
            <td>{{ formatDate(user.createdAt) }}</td>
            <td>
              <span :class="['status', user.disabled ? 'inactive' : 'active']">
                {{ user.disabled ? 'Vô hiệu hóa' : 'Hoạt động' }}
              </span>
            </td>
            <td>
              <button class="btn view-btn" @click="viewUserDetails(user)">
                Xem
              </button>
              <button 
                :class="['btn', user.disabled ? 'activate-btn' : 'disable-btn']"
                @click="toggleUserStatus(user)"
              >
                {{ user.disabled ? 'Kích hoạt' : 'Vô hiệu hóa' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-else-if="!isLoadingUsers" class="empty-state">
        Không tìm thấy người dùng nào.
      </div>
      
      <!-- Chi tiết người dùng -->
      <div v-if="selectedUser" class="modal">
        <div class="modal-content">
          <div class="modal-header">
            <h3>Thông tin người dùng</h3>
            <button class="close-btn" @click="selectedUser = null">&times;</button>
          </div>
          <div class="modal-body">
            <div class="user-info">
              <p><strong>Tên:</strong> {{ selectedUser.name || 'Chưa cập nhật' }}</p>
              <p><strong>Email:</strong> {{ selectedUser.email }}</p>
              <p><strong>Ngày đăng ký:</strong> {{ formatDate(selectedUser.createdAt) }}</p>
              <p><strong>Đăng nhập cuối:</strong> {{ formatDate(selectedUser.lastLogin) }}</p>
              <p><strong>Trạng thái:</strong> 
                <span :class="['status', selectedUser.disabled ? 'inactive' : 'active']">
                  {{ selectedUser.disabled ? 'Vô hiệu hóa' : 'Hoạt động' }}
                </span>
              </p>
            </div>
            
            <div class="user-actions">
              <button 
                :class="['btn', selectedUser.disabled ? 'activate-btn' : 'disable-btn']"
                @click="toggleUserStatus(selectedUser)"
              >
                {{ selectedUser.disabled ? 'Kích hoạt tài khoản' : 'Vô hiệu hóa tài khoản' }}
              </button>
              <button class="btn" @click="resetUserPassword(selectedUser)">
                Đặt lại mật khẩu
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Quản lý cảnh báo -->
    <div v-if="activeTab === 'alerts'" class="panel">
      <h2>Quản lý cảnh báo</h2>
      <div class="filters">
        <input 
          type="text" 
          v-model="alertSearchQuery" 
          placeholder="Tìm kiếm cảnh báo..." 
          @input="searchAlerts"
        />
        <select v-model="alertTypeFilter" @change="filterAlerts">
          <option value="all">Tất cả loại</option>
          <option value="fire">Cháy</option>
          <option value="intrusion">Đột nhập</option>
          <option value="motion">Chuyển động</option>
        </select>
        <select v-model="alertStatusFilter" @change="filterAlerts">
          <option value="all">Tất cả trạng thái</option>
          <option value="pending">Chưa xử lý</option>
          <option value="processing">Đang xử lý</option>
          <option value="resolved">Đã xử lý</option>
        </select>
      </div>
      
      <div v-if="isLoadingAlerts" class="loading">Đang tải...</div>
      
      <table v-else-if="filteredAlerts.length" class="data-table">
        <thead>
          <tr>
            <th>Thời gian</th>
            <th>Người dùng</th>
            <th>Loại cảnh báo</th>
            <th>Nội dung</th>
            <th>Trạng thái</th>
            <th>Thao tác</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="alert in filteredAlerts" :key="alert.id">
            <td>{{ formatDateTime(alert.timestamp) }}</td>
            <td>{{ getUserName(alert.userId) }}</td>
            <td>
              <span :class="['alert-type', alert.type]">
                {{ getAlertTypeName(alert.type) }}
              </span>
            </td>
            <td>{{ alert.message }}</td>
            <td>
              <span :class="['status', alert.status]">
                {{ getAlertStatusName(alert.status) }}
              </span>
            </td>
            <td>
              <button class="btn view-btn" @click="viewAlertDetails(alert)">Xem</button>
              <button 
                v-if="alert.status !== 'resolved'"
                class="btn resolve-btn" 
                @click="resolveAlert(alert)"
              >
                Đánh dấu đã xử lý
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-else-if="!isLoadingAlerts" class="empty-state">
        Không tìm thấy cảnh báo nào.
      </div>
      
      <!-- Chi tiết cảnh báo -->
      <div v-if="selectedAlert" class="modal">
        <div class="modal-content">
          <div class="modal-header">
            <h3>Chi tiết cảnh báo</h3>
            <button class="close-btn" @click="selectedAlert = null">&times;</button>
          </div>
          <div class="modal-body">
            <div class="alert-info">
              <p><strong>Loại cảnh báo:</strong> {{ getAlertTypeName(selectedAlert.type) }}</p>
              <p><strong>Thời gian:</strong> {{ formatDateTime(selectedAlert.timestamp) }}</p>
              <p><strong>Người dùng:</strong> {{ getUserName(selectedAlert.userId) }}</p>
              <p><strong>Nội dung:</strong> {{ selectedAlert.message }}</p>
              <p><strong>Trạng thái:</strong>
                <span :class="['status', selectedAlert.status]">
                  {{ getAlertStatusName(selectedAlert.status) }}
                </span>
              </p>
            </div>
            
            <div v-if="selectedAlert.status !== 'resolved'" class="alert-actions">
              <textarea 
                v-model="resolutionNotes"
                placeholder="Nhập ghi chú xử lý..."
              ></textarea>
              <button class="btn resolve-btn" @click="resolveSelectedAlert">
                Đánh dấu đã xử lý
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { db } from '../firebase';
import { 
  collection, getDocs, doc, updateDoc, 
  query, where, orderBy, serverTimestamp 
} from 'firebase/firestore';

export default {
  setup() {
    // State
    const users = ref([]);
    const alerts = ref([]);
    const activeTab = ref('dashboard');
    const isLoadingUsers = ref(true);
    const isLoadingAlerts = ref(true);
    const selectedUser = ref(null);
    const selectedAlert = ref(null);
    const userSearchQuery = ref('');
    const alertSearchQuery = ref('');
    const alertTypeFilter = ref('all');
    const alertStatusFilter = ref('all');
    const userSortField = ref('createdAt');
    const userSortDirection = ref('desc');
    const resolutionNotes = ref('');

    // Các tab
    const tabs = [
      { id: 'dashboard', name: 'Tổng quan' },
      { id: 'users', name: 'Người dùng' },
      { id: 'alerts', name: 'Cảnh báo' }
    ];

    // Fetch data
    const fetchUsers = async () => {
      isLoadingUsers.value = true;
      try {
        const querySnapshot = await getDocs(collection(db, "users"));
        users.value = querySnapshot.docs.map(doc => ({
          id: doc.id,
          ...doc.data()
        }));
      } catch (error) {
        console.error("Lỗi khi tải dữ liệu người dùng:", error);
      } finally {
        isLoadingUsers.value = false;
      }
    };

    const fetchAlerts = async () => {
      isLoadingAlerts.value = true;
      try {
        const alertsRef = collection(db, "alerts");
        const querySnapshot = await getDocs(
          query(alertsRef, orderBy("timestamp", "desc"))
        );
        alerts.value = querySnapshot.docs.map(doc => ({
          id: doc.id,
          ...doc.data(),
          status: doc.data().status || 'pending'
        }));
      } catch (error) {
        console.error("Lỗi khi tải dữ liệu cảnh báo:", error);
      } finally {
        isLoadingAlerts.value = false;
      }
    };

    // Computed
    const filteredUsers = computed(() => {
      let result = [...users.value];
      
      if (userSearchQuery.value.trim()) {
        const query = userSearchQuery.value.toLowerCase();
        result = result.filter(user => 
          (user.name && user.name.toLowerCase().includes(query)) ||
          (user.email && user.email.toLowerCase().includes(query))
        );
      }
      
      // Sắp xếp
      result.sort((a, b) => {
        let fieldA = a[userSortField.value];
        let fieldB = b[userSortField.value];
        
        if (fieldA && fieldA.toDate) fieldA = fieldA.toDate();
        if (fieldB && fieldB.toDate) fieldB = fieldB.toDate();
        
        if (userSortDirection.value === 'asc') {
          return fieldA > fieldB ? 1 : -1;
        } else {
          return fieldA < fieldB ? 1 : -1;
        }
      });
      
      return result;
    });

    const filteredAlerts = computed(() => {
      let result = [...alerts.value];
      
      if (alertSearchQuery.value.trim()) {
        const query = alertSearchQuery.value.toLowerCase();
        result = result.filter(alert => 
          (alert.message && alert.message.toLowerCase().includes(query))
        );
      }
      
      if (alertTypeFilter.value !== 'all') {
        result = result.filter(alert => alert.type === alertTypeFilter.value);
      }
      
      if (alertStatusFilter.value !== 'all') {
        result = result.filter(alert => alert.status === alertStatusFilter.value);
      }
      
      return result;
    });

    const unhandledAlerts = computed(() => {
      return alerts.value.filter(alert => alert.status !== 'resolved');
    });

    const newUsers = computed(() => {
      const date7DaysAgo = new Date();
      date7DaysAgo.setDate(date7DaysAgo.getDate() - 7);
      
      return users.value.filter(user => {
        if (!user.createdAt) return false;
        const createdDate = user.createdAt.toDate ? user.createdAt.toDate() : new Date(user.createdAt);
        return createdDate >= date7DaysAgo;
      }).length;
    });

    const todayAlerts = computed(() => {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      
      return alerts.value.filter(alert => {
        if (!alert.timestamp) return false;
        const alertDate = alert.timestamp.toDate ? alert.timestamp.toDate() : new Date(alert.timestamp);
        return alertDate >= today;
      }).length;
    });

    // Methods
    const formatDate = (date) => {
      if (!date) return 'N/A';
      const d = date.toDate ? date.toDate() : new Date(date);
      return d.toLocaleDateString('vi-VN');
    };

    const formatDateTime = (date) => {
      if (!date) return 'N/A';
      const d = date.toDate ? date.toDate() : new Date(date);
      return d.toLocaleDateString('vi-VN') + ' ' + d.toLocaleTimeString('vi-VN');
    };

    const searchUsers = () => {
      // Tìm kiếm được xử lý qua computed
    };

    const sortUsers = (field) => {
      if (userSortField.value === field) {
        userSortDirection.value = userSortDirection.value === 'asc' ? 'desc' : 'asc';
      } else {
        userSortField.value = field;
        userSortDirection.value = 'asc';
      }
    };

    const viewUserDetails = (user) => {
      selectedUser.value = user;
    };

    const toggleUserStatus = async (user) => {
      try {
        const userRef = doc(db, "users", user.id);
        await updateDoc(userRef, {
          disabled: !user.disabled
        });
        
        // Cập nhật trong danh sách
        const index = users.value.findIndex(u => u.id === user.id);
        if (index !== -1) {
          users.value[index].disabled = !users.value[index].disabled;
        }
        
        // Cập nhật nếu đang xem chi tiết
        if (selectedUser.value && selectedUser.value.id === user.id) {
          selectedUser.value.disabled = !selectedUser.value.disabled;
        }
      } catch (error) {
        console.error("Lỗi khi cập nhật trạng thái người dùng:", error);
      }
    };

    const resetUserPassword = (user) => {
      // Thực hiện đặt lại mật khẩu (có thể là gửi email)
      alert(`Đã gửi email đặt lại mật khẩu cho ${user.email}`);
    };

    const searchAlerts = () => {
      // Tìm kiếm được xử lý qua computed
    };

    const filterAlerts = () => {
      // Lọc được xử lý qua computed
    };

    const getAlertTypeName = (type) => {
      const types = {
        fire: 'Cháy',
        intrusion: 'Đột nhập',
        motion: 'Chuyển động'
      };
      return types[type] || type;
    };

    const getAlertStatusName = (status) => {
      const statuses = {
        pending: 'Chưa xử lý',
        processing: 'Đang xử lý',
        resolved: 'Đã xử lý'
      };
      return statuses[status] || status;
    };

    const getUserName = (userId) => {
      const user = users.value.find(u => u.id === userId);
      return user ? (user.name || user.email) : 'Không tìm thấy';
    };

    const viewAlertDetails = (alert) => {
      selectedAlert.value = alert;
      resolutionNotes.value = '';
    };

    const resolveAlert = async (alert) => {
      try {
        const alertRef = doc(db, "alerts", alert.id);
        await updateDoc(alertRef, {
          status: 'resolved',
          resolvedAt: serverTimestamp(),
          resolvedBy: 'Admin' // Hoặc lấy thông tin admin hiện tại
        });
        
        // Cập nhật trong danh sách
        const index = alerts.value.findIndex(a => a.id === alert.id);
        if (index !== -1) {
          alerts.value[index].status = 'resolved';
        }
      } catch (error) {
        console.error("Lỗi khi cập nhật trạng thái cảnh báo:", error);
      }
    };

    const resolveSelectedAlert = async () => {
      if (!selectedAlert.value) return;
      
      try {
        const alertRef = doc(db, "alerts", selectedAlert.value.id);
        await updateDoc(alertRef, {
          status: 'resolved',
          resolvedAt: serverTimestamp(),
          resolvedBy: 'Admin', // Hoặc lấy thông tin admin hiện tại
          notes: resolutionNotes.value
        });
        
        // Cập nhật trong danh sách
        const index = alerts.value.findIndex(a => a.id === selectedAlert.value.id);
        if (index !== -1) {
          alerts.value[index].status = 'resolved';
          alerts.value[index].notes = resolutionNotes.value;
        }
        
        // Đóng modal
        selectedAlert.value = null;
      } catch (error) {
        console.error("Lỗi khi cập nhật trạng thái cảnh báo:", error);
      }
    };

    // Lifecycle
    onMounted(() => {
      fetchUsers();
      fetchAlerts();
    });

    return {
      // State
      users,
      alerts,
      activeTab,
      tabs,
      isLoadingUsers,
      isLoadingAlerts,
      selectedUser,
      selectedAlert,
      userSearchQuery,
      alertSearchQuery,
      alertTypeFilter,
      alertStatusFilter,
      userSortField,
      userSortDirection,
      resolutionNotes,
      
      // Computed
      filteredUsers,
      filteredAlerts,
      unhandledAlerts,
      newUsers,
      todayAlerts,
      
      // Methods
      formatDate,
      formatDateTime,
      searchUsers,
      sortUsers,
      viewUserDetails,
      toggleUserStatus,
      resetUserPassword,
      searchAlerts,
      filterAlerts,
      getAlertTypeName,
      getAlertStatusName,
      getUserName,
      viewAlertDetails,
      resolveAlert,
      resolveSelectedAlert
    };
  }
};
</script>

<style scoped>
.admin-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

.page-title {
  font-size: 24px;
  margin-bottom: 20px;
  color: #333;
}

/* Tabs */
.tab-navigation {
  display: flex;
  margin-bottom: 20px;
  border-bottom: 1px solid #ddd;
}

.tab-btn {
  padding: 10px 15px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  color: #666;
}

.tab-btn.active {
  color: #4285f4;
  border-bottom: 2px solid #4285f4;
  font-weight: bold;
}

/* Panels */
.panel {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.panel h2 {
  margin-top: 0;
  font-size: 20px;
  color: #333;
  margin-bottom: 15px;
}

/* Stats */
.stats-summary {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.stat-item {
  background: #f9f9f9;
  padding: 15px;
  border-radius: 6px;
  border-left: 4px solid #4285f4;
}

/* Tables */
.data-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px;
}

.data-table th,
.data-table td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.data-table th {
  background-color: #f5f5f5;
  font-weight: 600;
  cursor: pointer;
}

.data-table th:hover {
  background-color: #e9e9e9;
}

/* Search and filters */
.search-bar,
.filters {
  margin-bottom: 15px;
}

.search-bar input,
.filters input,
.filters select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.filters {
  display: flex;
  gap: 10px;
}

/* Status badges */
.status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  display: inline-block;
}

.status.active {
  background-color: #d4edda;
  color: #155724;
}

.status.inactive {
  background-color: #f8d7da;
  color: #721c24;
}

.status.pending {
  background-color: #fff3cd;
  color: #856404;
}

.status.processing {
  background-color: #cce5ff;
  color: #004085;
}

.status.resolved {
  background-color: #d4edda;
  color: #155724;
}

/* Alert types */
.alert-type {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.alert-type.fire {
  background-color: #ffecec;
  color: #e63946;
}

.alert-type.intrusion {
  background-color: #e9ecef;
  color: #343a40;
}

.alert-type.motion {
  background-color: #e6f7ff;
  color: #0077b6;
}

/* Buttons */
.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin-right: 5px;
  background-color: #e9ecef;
  color: #212529;
}

.btn:hover {
  opacity: 0.9;
}

.view-btn {
  background-color: #4285f4;
  color: white;
}

.resolve-btn {
  background-color: #34a853;
  color: white;
}

.disable-btn {
  background-color: #ea4335;
  color: white;
}

.activate-btn {
  background-color: #34a853;
  color: white;
}

/* Modal */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  max-height: 90%;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 20px;
}

.user-info,
.alert-info {
  margin-bottom: 20px;
}

.user-info p,
.alert-info p {
  margin: 8px 0;
}

.user-actions,
.alert-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.alert-actions textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-bottom: 10px;
  resize: vertical;
  min-height: 80px;
}

/* Loading */
.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}

/* Empty state */
.empty-state {
  text-align: center;
  padding: 30px;
  color: #666;
  background-color: #f9f9f9;
  border-radius: 6px;
  margin-top: 15px;
}
</style>