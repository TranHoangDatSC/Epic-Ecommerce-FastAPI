import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';

@Component({
  selector: 'app-moderator-layout',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './moderator-layout.html',
  styleUrl: './moderator-layout.scss'
})
export class ModeratorLayoutComponent {
  constructor(private router: Router) {}

  logout(): void {
    this.router.navigate(['/auth/login']);
  }
}
