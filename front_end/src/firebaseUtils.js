// Tạo file hỗ trợ xử lý thông báo lỗi Firebase
export const getFirebaseErrorMessage = (errorCode) => {
  switch (errorCode) {
    // Lỗi xác thực
    case "auth/email-already-in-use":
      return "Email này đã được sử dụng bởi tài khoản khác.";
    case "auth/invalid-email":
      return "Email không hợp lệ.";
    case "auth/user-disabled":
      return "Tài khoản này đã bị vô hiệu hóa.";
    case "auth/user-not-found":
      return "Không tìm thấy tài khoản với email này.";
    case "auth/wrong-password":
      return "Mật khẩu không chính xác.";
    case "auth/weak-password":
      return "Mật khẩu quá yếu. Vui lòng chọn mật khẩu mạnh hơn.";
    case "auth/operation-not-allowed":
      return "Hoạt động này không được cho phép.";
    case "auth/account-exists-with-different-credential":
      return "Email này đã được liên kết với một phương thức đăng nhập khác.";
    case "auth/invalid-credential":
      return "Thông tin đăng nhập không hợp lệ.";
    case "auth/invalid-verification-code":
      return "Mã xác minh không hợp lệ.";
    case "auth/invalid-verification-id":
      return "ID xác minh không hợp lệ.";
    case "auth/requires-recent-login":
      return "Hành động này yêu cầu bạn đăng nhập lại.";
    case "auth/missing-email":
      return "Vui lòng cung cấp email.";
    case "auth/missing-password":
      return "Vui lòng nhập mật khẩu.";

    // Lỗi mạng
    case "auth/network-request-failed":
      return "Lỗi kết nối mạng. Vui lòng kiểm tra kết nối internet của bạn.";
    case "auth/timeout":
      return "Yêu cầu đã hết thời gian. Vui lòng thử lại.";

    // Lỗi giới hạn
    case "auth/too-many-requests":
      return "Quá nhiều yêu cầu không thành công. Vui lòng thử lại sau.";

    // Lỗi Firestore
    case "firestore/permission-denied":
      return "Bạn không có quyền truy cập vào dữ liệu này.";
    case "firestore/unavailable":
      return "Dịch vụ Firestore hiện không khả dụng. Vui lòng thử lại sau.";
    case "firestore/not-found":
      return "Không tìm thấy tài liệu yêu cầu.";
    case "firestore/data-loss":
      return "Đã xảy ra lỗi mất dữ liệu không khắc phục được.";
    case "firestore/cancelled":
      return "Hoạt động đã bị hủy.";
    case "firestore/invalid-argument":
      return "Đối số không hợp lệ được cung cấp cho hoạt động.";

    // Các lỗi chung
    default:
      return "Đã xảy ra lỗi không xác định. Vui lòng thử lại sau.";
  }
};

// Hàm kiểm tra và xác thực form
export const validateForm = (formData, requiredFields) => {
  const errors = {};

  // Kiểm tra các trường bắt buộc
  requiredFields.forEach((field) => {
    if (!formData[field] || formData[field].trim() === "") {
      errors[field] = "Trường này là bắt buộc";
    }
  });

  // Kiểm tra email nếu có
  if (formData.email && !isValidEmail(formData.email)) {
    errors.email = "Email không hợp lệ";
  }

  // Kiểm tra mật khẩu nếu có
  if (formData.password) {
    if (formData.password.length < 6) {
      errors.password = "Mật khẩu phải có ít nhất 6 ký tự";
    }

    // Kiểm tra xác nhận mật khẩu nếu có
    if (
      formData.confirmPassword &&
      formData.password !== formData.confirmPassword
    ) {
      errors.confirmPassword = "Mật khẩu không khớp";
    }
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};

// Hàm kiểm tra email hợp lệ
export const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// Hàm tạo ID ngẫu nhiên
export const generateId = (length = 20) => {
  const chars =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  let result = "";
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
};

// Hàm định dạng ngày giờ
export const formatDateTime = (timestamp) => {
  if (!timestamp) return "";

  const date = timestamp instanceof Date ? timestamp : timestamp.toDate();

  return new Intl.DateTimeFormat("vi-VN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  }).format(date);
};

// Hàm chuyển đổi timestamp thành đối tượng Date
export const timestampToDate = (timestamp) => {
  if (!timestamp) return null;
  return timestamp instanceof Date ? timestamp : timestamp.toDate();
};
