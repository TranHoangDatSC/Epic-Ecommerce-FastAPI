import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UIService } from '../../core/services/ui.service';

@Component({
  selector: 'app-contact',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './contact.html',
  styleUrls: ['./contact.scss']
})
export class ContactComponent {
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

  constructor(private uiService: UIService) {}

  sendMessage() {
    // Basic validation
    if (!this.formData.fullName || !this.formData.email || !this.formData.message) {
      this.uiService.showError('Vui lòng điền đầy đủ các thông tin bắt buộc!', 'Thông báo');
      return;
    }

    // Simulate API call
    console.log('Sending message:', this.formData);
    
    this.uiService.showModal({
      title: 'Đã gửi yêu cầu!',
      message: 'Cảm ơn bạn đã liên hệ. Đội ngũ OldShop sẽ phản hồi bạn sớm nhất có thể qua Email hoặc Số điện thoại.',
      type: 'success'
    });

    // Reset form
    this.formData = {
      fullName: '',
      email: '',
      phone: '',
      subject: '',
      message: ''
    };
  }
}