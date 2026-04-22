import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UIService } from '../../core/services/ui.service';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-contact',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './contact.html',
  styleUrls: ['./contact.scss']
})
export class ContactComponent {
  isLoading = false;

  // THÊM LẠI ĐOẠN NÀY ĐỂ FIX LỖI TS2339
  contactInfo = {
    office: 'Số 123, Đường ABC, Quận Ninh Kiều, Cần Thơ',
    email: 'contact@oldshop.com',
    phone: '0987.654.321',
    messenger: 'm.me/oldshop.secondhand'
  };

  formData = {
    fullName: '',
    email: '',
    phone: '',
    subject: '',
    message: ''
  };

  constructor(private uiService: UIService, private cdr: ChangeDetectorRef) {}

  async sendMessage() {
    // 1. Kiểm tra đầu vào
    if (!this.formData.fullName || !this.formData.email || !this.formData.message) {
      this.uiService.showError('Vui lòng điền đầy đủ các thông tin bắt buộc!', 'Thông báo');
      return;
    }

    this.isLoading = true;

    try {
      // 2. Chuyển sang URLSearchParams
      const payload = new URLSearchParams();
      payload.append('fullName', this.formData.fullName);
      payload.append('email', this.formData.email);
      payload.append('phone', this.formData.phone || 'N/A');
      payload.append('subject', this.formData.subject || 'Liên hệ từ website');
      payload.append('message', this.formData.message);

      // 3. Gửi POST (Dùng fetch vì mode no-cors xử lý Google Script tốt hơn HttpClient của Angular trong một số case local)
      await fetch(environment.googleScriptContact, {
        method: 'POST',
        body: payload,
        mode: 'no-cors', 
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });

      // 4. Thành công
      this.uiService.showModal({
        title: 'Đã gửi yêu cầu!',
        message: 'Cảm ơn bạn đã liên hệ. Đội ngũ OldShop sẽ phản hồi bạn sớm nhất.',
        type: 'success'
        
      });

      // Reset form
      this.formData = { fullName: '', email: '', phone: '', subject: '', message: '' };

    } catch (error) {
      console.error('Lỗi gửi contact:', error);
      this.uiService.showError('Đã có lỗi xảy ra, vui lòng thử lại sau!', 'Lỗi');
      this.cdr.detectChanges();
    } finally {
      this.isLoading = false;
      this.cdr.detectChanges();
    }
  }
}