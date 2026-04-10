import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AdminService } from '../../../shared/services/admin.service';

@Component({
  selector: 'sellerhub-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss'
})
export class SellerHubDashboardComponent implements OnInit {
  stats: any = {
    total_users: 0,
    total_orders: 0,
    pending_products: 0,
    total_revenue: 0
  };
  isLoading = true;

  constructor(private adminService: AdminService) {}

  ngOnInit(): void {
    this.loadStats();
  }

  loadStats() {
    this.isLoading = true;
    this.adminService.getStats().subscribe({
      next: (data) => {
        this.stats = data;
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error loading stats:', err);
        this.isLoading = false;
      }
    });
  }

  formatRevenue(val: number): string {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);
  }
}
