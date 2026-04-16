import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

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
  private modalSubject = new Subject<ModalConfig>();
  modal$ = this.modalSubject.asObservable();

  showModal(config: ModalConfig) {
    this.modalSubject.next(config);
    
    setTimeout(() => {
      const modalElement = document.getElementById('globalNotificationModal');
      if (modalElement) {
        try {
          const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
          modal.show();
        } catch (e) {
          console.error("Lỗi khi mở modal:", e);
        }
      } else {
        console.warn("Global Notification Modal không tìm thấy trong DOM!");
      }
    }, 100); 
  }

  showSuccess(message: string, title: string = 'Thành công!') {
    this.showModal({ title, message, type: 'success' });
  }

  showError(message: string, title: string = 'Lỗi!') {
    this.showModal({ title, message, type: 'error' });
  }
}