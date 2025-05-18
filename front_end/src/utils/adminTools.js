// Đây là file công cụ để nâng cấp quyền người dùng lên admin
// Lưu nó tại src/utils/adminTools.js

import { db } from "../firebase";
import { doc, updateDoc, getDoc } from "firebase/firestore";

/**
 * Nâng cấp một người dùng thành admin
 * @param {string} userId - ID của người dùng cần nâng cấp
 * @returns {Promise} - Kết quả của hành động
 */
export const upgradeToAdmin = async (userId) => {
  if (!userId) {
    throw new Error("Bạn cần cung cấp ID người dùng");
  }

  try {
    // Kiểm tra xem người dùng có tồn tại không
    const userDoc = await getDoc(doc(db, "users", userId));
    if (!userDoc.exists()) {
      throw new Error("Không tìm thấy người dùng với ID này");
    }

    // Cập nhật thông tin
    await updateDoc(doc(db, "users", userId), {
      role: "admin",
      updatedAt: new Date(),
    });

    return {
      success: true,
      message: "Người dùng đã được nâng cấp thành admin thành công",
    };
  } catch (error) {
    console.error("Lỗi khi nâng cấp quyền admin:", error);
    return {
      success: false,
      message: `Không thể nâng cấp: ${error.message}`,
    };
  }
};

/**
 * Hạ quyền admin của một người dùng
 * @param {string} userId - ID của người dùng
 * @returns {Promise} - Kết quả của hành động
 */
export const revokeAdminRights = async (userId) => {
  if (!userId) {
    throw new Error("Bạn cần cung cấp ID người dùng");
  }

  try {
    // Kiểm tra xem người dùng có tồn tại không
    const userDoc = await getDoc(doc(db, "users", userId));
    if (!userDoc.exists()) {
      throw new Error("Không tìm thấy người dùng với ID này");
    }

    // Cập nhật thông tin
    await updateDoc(doc(db, "users", userId), {
      role: "user",
      updatedAt: new Date(),
    });

    return {
      success: true,
      message: "Quyền admin đã bị thu hồi thành công",
    };
  } catch (error) {
    console.error("Lỗi khi thu hồi quyền admin:", error);
    return {
      success: false,
      message: `Không thể thu hồi quyền: ${error.message}`,
    };
  }
};
