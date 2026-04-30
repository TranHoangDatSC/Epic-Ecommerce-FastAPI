import { Injectable, ApplicationRef, inject } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

declare var bootstrap: any;

export interface ModalConfig {
  title: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  confirmText?: string;
  cancelText?: string;
}

@Injectable({ providedIn: 'root' })
export class UIService {
  // Dùng BehaviorSubject thay vì Subject để Modal luôn nhận được data kể cả khi render chậm
  private modalSubject = new BehaviorSubject<ModalConfig | null>(null);
  modal$ = this.modalSubject.asObservable();
  
  // Vũ khí hạng nặng ép Angular cập nhật UI
  private appRef = inject(ApplicationRef);

  showModal(config: ModalConfig) {
    // Tách luồng tuyệt đối ra khỏi các sự kiện đang chạy để chặn đứng lỗi NG0100
    setTimeout(() => {
      // 1. Bơm dữ liệu (Title, Message, Type) vào Modal
      this.modalSubject.next(config);
      
      // 2. ÉP ANGULAR RENDER TOÀN BỘ DOM NGAY LẬP TỨC (Vẽ Icon, vẽ Text)
      this.appRef.tick(); 

      // 3. Đợi DOM vẽ xong xuôi 100% rồi mới gọi Bootstrap bật lên
      const modalElement = document.getElementById('globalNotificationModal');
      if (modalElement) {
        try {
          const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
          modal.show();
        } catch (e) {
          console.error("Lỗi khi mở modal:", e);
        }
      } else {
        console.warn("Không tìm thấy globalNotificationModal trong HTML!");
      }
    }, 50); // Chỉ cần delay 50ms là đủ mượt
  }

  showSuccess(message: string, title: string = 'Thành công') {
    this.showModal({ title, message, type: 'success' });
  }

  showError(message: string, title: string = 'Lỗi') {
    this.showModal({ title, message, type: 'error' });
  }

  showInfo(message: string, title: string = 'Thông báo') {
    this.showModal({ title, message, type: 'info' });
  }
}