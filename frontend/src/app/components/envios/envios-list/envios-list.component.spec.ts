import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EnviosListComponent } from './envios-list.component';

describe('EnviosListComponent', () => {
  let component: EnviosListComponent;
  let fixture: ComponentFixture<EnviosListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EnviosListComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EnviosListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
