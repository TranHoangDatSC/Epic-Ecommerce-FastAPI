import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

export interface ModalConfig {
  title: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  confirmText?: string;
  cancelText?: string;
}

@Injectable({
  providedIn: 'root'
})
export class UIService {
  private modalSubject = new Subject<ModalConfig>();
  modal$ = this.modalSubject.asObservable();

  showModal(config: ModalConfig) {
    this.modalSubject.next(config);
  }

  showSuccess(message: string, title: string = 'Thành công!') {
    this.showModal({ title, message, type: 'success' });
  }

  showError(message: string, title: string = 'Lỗi!') {
    this.showModal({ title, message, type: 'error' });
  }
}
