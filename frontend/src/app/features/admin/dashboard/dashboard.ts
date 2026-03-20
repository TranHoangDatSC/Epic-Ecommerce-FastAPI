import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BaseChartDirective } from 'ng2-charts';
import { ViewChild } from '@angular/core';
import { ChartConfiguration } from 'chart.js';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule, BaseChartDirective],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss'
})

export class AdminDashboardComponent implements OnInit {
  currentTime = new Date().toLocaleTimeString('en-US', {
  hour: '2-digit',
  minute: '2-digit',
  second: '2-digit',
  hour12: true
  });

  stats = {
    processedToday: 15
  };

  ngOnInit() {}

@ViewChild(BaseChartDirective) chart?: BaseChartDirective;

lineDataThisWeek = [5, 8, 4, 9, 6, 12, 10];
lineDataLastWeek = [3, 6, 7, 5, 8, 9, 11];

onWeekChange(e: any) {
  const v = e.target.value;

  this.lineData.datasets[0].data =
    v === 'this' ? this.lineDataThisWeek : this.lineDataLastWeek;

  this.chart?.update();
};

lineData: ChartConfiguration<'line'>['data'] = {
  labels: ['T2','T3','T4','T5','T6','T7','CN'],
  datasets: [
    {      
      label: 'Doanh thu',
      data: this.lineDataThisWeek,
      borderColor: '#6366f1',
      backgroundColor: 'rgba(99,102,241,0.2)',
      fill: true,
      tension: 0.4,
      pointBackgroundColor: 'rgba(99,102,241,0.4)',
      pointBorderColor: 'rgba(99,102,241,1)',
      pointRadius: 5
    }
  ]
};

lineOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top' as const,
      display: true,
      labels: {
      boxWidth: 30,
      padding: 15
    }
      
    }
  }
};

pieRawData = [40,30,30];

pieData: ChartConfiguration<'doughnut'>['data'] = {
  labels: ['Điện tử', 'Gia dụng', 'Thời trang'],
  datasets: [
    {
      label: 'Danh mục',
      data: this.pieRawData,
      backgroundColor: [
        '#6366f1', 
        '#f59e0b', 
        '#22c55e'  
      ],
    }
  ]
};

pieOptions: ChartConfiguration<'doughnut'>['options'] = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '70%',
  plugins: {
    legend: {
      position: 'bottom' as const,
      labels: {
      boxWidth: 30,
      padding: 15
      }
    }
  }
};
}