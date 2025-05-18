// Đặt file này tại src/router/authGuard.js

import { auth } from "../firebase";
import { getDoc, doc } from "firebase/firestore";
import { db } from "../firebase";

/**
 * Middleware kiểm tra quyền admin
 * @returns {Promise} - Trả về true nếu người dùng có quyền admin, false nếu không
 */
export const isAdmin = async () => {
  return new Promise((resolve) => {
    const unsubscribe = auth.onAuthStateChanged(async (user) => {
      unsubscribe(); // Hủy đăng ký listener ngay sau khi kiểm tra

      if (user) {
        try {
          // Lấy thông tin người dùng từ Firestore
          const userDoc = await getDoc(doc(db, "users", user.uid));

          if (userDoc.exists() && userDoc.data().role === "admin") {
            resolve(true); // Người dùng có quyền admin
          } else {
            resolve(false); // Người dùng không có quyền admin
          }
        } catch (error) {
          console.error("Lỗi khi kiểm tra quyền admin:", error);
          resolve(false);
        }
      } else {
        resolve(false); // Người dùng chưa đăng nhập
      }
    });
  });
};

/**
 * Middleware kiểm tra xem người dùng đã đăng nhập chưa
 * @returns {Promise} - Trả về true nếu người dùng đã đăng nhập, false nếu chưa
 */
export const isAuthenticated = () => {
  return new Promise((resolve) => {
    const unsubscribe = auth.onAuthStateChanged((user) => {
      unsubscribe();
      resolve(!!user);
    });
  });
};
