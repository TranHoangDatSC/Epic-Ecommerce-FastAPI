import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-contact',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './contact.html',
  styleUrl: './contact.scss',
})
export class ContactComponent {
  contactInfo = {
    office: '123 A, Sài Gòn',
    email: 'hotro@chocu.vn',
    phone: '0123 456 789',
    messenger: 'm.me/chocuonline',
  };

  sendMessage() {
    alert('Tin nhắn của bạn đã được gửi!');
  }
}
