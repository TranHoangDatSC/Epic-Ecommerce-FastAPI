import { Component, ChangeDetectorRef } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'sellproduct',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './sellproduct.html',
  styleUrls: ['./sellproduct.scss']
})
export class PostProductComponent {
  productForm: FormGroup;
  previewUrls: string[] = [];
  selectedFiles: File[] = [];

  constructor(
    private fb: FormBuilder,
    private cdr: ChangeDetectorRef
  ) {
    this.productForm = this.fb.group({
      name: [''],
      category: ['electronics'],
      price: [0],
      quantity: [1],
      videoUrl: [''],
      description: ['']
    });
  }

  onFileChange(event: any) {
    const files: FileList = event.target.files;

    if (!files || files.length === 0) return;

    const newFiles = Array.from(files);

    if (this.selectedFiles.length + newFiles.length > 3) {
      alert('Chỉ được tối đa 3 ảnh');
      return;
    }

    for (let file of newFiles) {
      this.selectedFiles.push(file); 

      const reader = new FileReader();

      reader.onload = (e: any) => {
        this.previewUrls.push(e.target.result); 
        this.cdr.detectChanges();
      };

      reader.readAsDataURL(file);
    }

    event.target.value = '';
  }

  removeImage(index: number) {
    this.previewUrls.splice(index, 1);
    this.selectedFiles.splice(index, 1);
  }

  onSubmit() {
    console.log('Form:', this.productForm.value);
    console.log('Images:', this.selectedFiles);

    alert('Đăng bán thành công!');
  }
}