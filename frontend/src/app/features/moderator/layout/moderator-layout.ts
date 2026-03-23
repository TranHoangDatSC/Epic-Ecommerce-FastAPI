import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-moderator-layout',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './moderator-layout.html',
  styleUrl: './moderator-layout.scss'
})
export class ModeratorLayoutComponent {
  private authService = inject(AuthService);

  constructor() {}

  logout() {
    this.authService.logout();
  }
}