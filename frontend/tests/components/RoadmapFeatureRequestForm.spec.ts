/**
 * Tests for RoadmapFeatureRequestForm component.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import RoadmapFeatureRequestForm from '@/components/RoadmapFeatureRequestForm.vue';
import * as roadmapService from '@/services/roadmapService';

// Mock roadmap service
vi.mock('@/services/roadmapService', () => ({
  getFeatureRequestModules: vi.fn(),
  createFeatureRequest: vi.fn(),
}));

describe('RoadmapFeatureRequestForm', () => {
  // Helper to mount component with proper stubs
  const mountComponent = (
    props: Partial<{ show: boolean }> = {},
    options: Record<string, unknown> = {},
  ) => {
    return mount(RoadmapFeatureRequestForm, {
      props: {
        show: true,
        ...props,
      },
      global: {
        stubs: {
          UnnnicModal: {
            template: '<div class="unnnic-modal-stub"><slot /></div>',
          },
          ...(options.stubs as Record<string, unknown>),
        },
      },
      ...options,
    });
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render when show prop is true', () => {
    const wrapper = mountComponent();
    expect(wrapper.find('.feature-request-form').exists()).toBe(true);
  });

  it('should not render when show prop is false', () => {
    const wrapper = mountComponent({ show: false });
    expect(wrapper.find('.feature-request-form').exists()).toBe(false);
  });

  it('should load modules when modal opens', async () => {
    const mockModules = {
      modules: [
        { id: 'nexus', name: 'Nexus', itemCount: 5 },
        { id: 'engage', name: 'Engage', itemCount: 3 },
      ],
    };

    vi.mocked(roadmapService.getFeatureRequestModules).mockResolvedValue(
      mockModules,
    );

    const wrapper = mountComponent();

    // Wait for modules to load
    await wrapper.vm.$nextTick();
    await new Promise((resolve) => setTimeout(resolve, 0));

    expect(roadmapService.getFeatureRequestModules).toHaveBeenCalled();
  });

  it('should emit close event when close button clicked', async () => {
    const wrapper = mountComponent();

    // Find cancel button and click
    const cancelButton = wrapper.findAll('button').find((btn) =>
      btn.text().includes('Cancel'),
    );

    if (cancelButton) {
      await cancelButton.trigger('click');
      expect(wrapper.emitted('close')).toBeTruthy();
    }
  });

  it('should validate required fields', async () => {
    const wrapper = mountComponent();

    // Get the form instance
    const vm = wrapper.vm as {
      form: { moduleId: string; title: string; description: string; contactEmail: string; website: string };
      errors: Record<string, string>;
      validateForm: () => boolean;
    };

    // Set incomplete form data
    vm.form = {
      moduleId: '',
      title: '',
      description: '',
      contactEmail: '',
      website: '',
    };

    // Trigger validation
    const isValid = vm.validateForm();

    expect(isValid).toBe(false);
    expect(vm.errors.moduleId).toBeTruthy();
    expect(vm.errors.title).toBeTruthy();
    expect(vm.errors.description).toBeTruthy();
    expect(vm.errors.contactEmail).toBeTruthy();
  });

  it('should submit form successfully', async () => {
    const mockResponse = {
      success: true,
      issueKey: 'NEXUS-123',
      issueUrl: 'https://test.atlassian.net/browse/NEXUS-123',
      leaderNotificationStatus: 'SENT',
      message: 'Feature request submitted successfully',
    };

    vi.mocked(roadmapService.getFeatureRequestModules).mockResolvedValue({
      modules: [{ id: 'nexus', name: 'Nexus', itemCount: 5 }],
    });
    vi.mocked(roadmapService.createFeatureRequest).mockResolvedValue(
      mockResponse,
    );

    const wrapper = mountComponent();

    const vm = wrapper.vm as {
      form: { moduleId: string; title: string; description: string; contactEmail: string; website: string };
      errors: Record<string, string>;
      validateForm: () => boolean;
    };

    // Fill form with valid data
    vm.form = {
      moduleId: 'nexus',
      title: 'Test Feature Request',
      description: 'This is a detailed description of the feature request.',
      contactEmail: 'user@example.com',
      website: '',
    };

    // Submit form
    await vm.handleSubmit();
    await wrapper.vm.$nextTick();

    expect(roadmapService.createFeatureRequest).toHaveBeenCalled();
    expect(wrapper.emitted('submitted')).toBeTruthy();
    expect(vm.issueKey).toBe('NEXUS-123');
  });

  it('should handle submission error', async () => {
    const error = {
      response: {
        data: {
          message: 'Validation failed',
        },
      },
    };

    vi.mocked(roadmapService.getFeatureRequestModules).mockResolvedValue({
      modules: [{ id: 'nexus', name: 'Nexus', itemCount: 5 }],
    });
    vi.mocked(roadmapService.createFeatureRequest).mockRejectedValue(error);

    const wrapper = mountComponent();

    const vm = wrapper.vm as {
      form: { moduleId: string; title: string; description: string; contactEmail: string; website: string };
      errors: Record<string, string>;
      validateForm: () => boolean;
    };

    vm.form = {
      moduleId: 'nexus',
      title: 'Test Feature',
      description: 'Test description for this feature request.',
      contactEmail: 'user@example.com',
      website: '',
    };

    await vm.handleSubmit();
    await wrapper.vm.$nextTick();

    expect(vm.errorMessage).toBe('Validation failed');
  });

  it('should validate email format', async () => {
    const wrapper = mountComponent();

    const vm = wrapper.vm as {
      form: { moduleId: string; title: string; description: string; contactEmail: string; website: string };
      errors: Record<string, string>;
      validateForm: () => boolean;
    };

    vm.form = {
      moduleId: 'nexus',
      title: 'Test',
      description: 'Test description',
      contactEmail: 'invalid-email',
      website: '',
    };

    const isValid = vm.validateForm();

    expect(isValid).toBe(false);
    expect(vm.errors.contactEmail).toBeTruthy();
  });

  it('should validate title length constraints', async () => {
    const wrapper = mountComponent();

    const vm = wrapper.vm as {
      form: { moduleId: string; title: string; description: string; contactEmail: string; website: string };
      errors: Record<string, string>;
      validateForm: () => boolean;
    };

    // Test too short
    vm.form = {
      moduleId: 'nexus',
      title: 'AB',
      description: 'Test description long enough',
      contactEmail: 'user@example.com',
      website: '',
    };

    let isValid = vm.validateForm();
    expect(isValid).toBe(false);
    expect(vm.errors.title).toContain('at least 3 characters');

    // Test too long
    vm.form.title = 'A'.repeat(201);
    isValid = vm.validateForm();
    expect(isValid).toBe(false);
    expect(vm.errors.title).toContain('at most 200 characters');
  });

  it('should validate description length constraints', async () => {
    const wrapper = mountComponent();

    const vm = wrapper.vm as {
      form: { moduleId: string; title: string; description: string; contactEmail: string; website: string };
      errors: Record<string, string>;
      validateForm: () => boolean;
    };

    // Test too short
    vm.form = {
      moduleId: 'nexus',
      title: 'Test Title',
      description: 'Short',
      contactEmail: 'user@example.com',
      website: '',
    };

    let isValid = vm.validateForm();
    expect(isValid).toBe(false);
    expect(vm.errors.description).toContain('at least 10 characters');

    // Test too long
    vm.form.description = 'A'.repeat(5001);
    isValid = vm.validateForm();
    expect(isValid).toBe(false);
    expect(vm.errors.description).toContain('at most 5000 characters');
  });

  it('should handle rate limit error (429)', async () => {
    const error = {
      response: {
        status: 429,
        data: {
          message: 'Rate limit exceeded',
        },
        headers: {
          'retry-after': '60',
        },
      },
    };

    vi.mocked(roadmapService.getFeatureRequestModules).mockResolvedValue({
      modules: [{ id: 'nexus', name: 'Nexus', itemCount: 5 }],
    });
    vi.mocked(roadmapService.createFeatureRequest).mockRejectedValue(error);

    const wrapper = mountComponent();

    const vm = wrapper.vm as {
      form: { moduleId: string; title: string; description: string; contactEmail: string; website: string };
      errorMessage: string;
      handleSubmit: () => Promise<void>;
    };

    vm.form = {
      moduleId: 'nexus',
      title: 'Test Feature',
      description: 'Test description for this feature request.',
      contactEmail: 'user@example.com',
      website: '',
    };

    await vm.handleSubmit();
    await wrapper.vm.$nextTick();

    expect(vm.errorMessage).toContain('wait 60 seconds');
  });

  it('should handle server error (500+)', async () => {
    const error = {
      response: {
        status: 500,
        data: {},
      },
    };

    vi.mocked(roadmapService.getFeatureRequestModules).mockResolvedValue({
      modules: [{ id: 'nexus', name: 'Nexus', itemCount: 5 }],
    });
    vi.mocked(roadmapService.createFeatureRequest).mockRejectedValue(error);

    const wrapper = mountComponent();

    const vm = wrapper.vm as {
      form: { moduleId: string; title: string; description: string; contactEmail: string; website: string };
      errorMessage: string;
      handleSubmit: () => Promise<void>;
    };

    vm.form = {
      moduleId: 'nexus',
      title: 'Test Feature',
      description: 'Test description for this feature request.',
      contactEmail: 'user@example.com',
      website: '',
    };

    await vm.handleSubmit();
    await wrapper.vm.$nextTick();

    expect(vm.errorMessage).toContain('Service temporarily unavailable');
  });

  it('should handle module loading error', async () => {
    vi.mocked(roadmapService.getFeatureRequestModules).mockRejectedValue(
      new Error('Network error'),
    );

    const wrapper = mountComponent();

    // Wait for modules to attempt load
    await wrapper.vm.$nextTick();
    await new Promise((resolve) => setTimeout(resolve, 0));

    const vm = wrapper.vm as {
      errorMessage: string;
      modules: unknown[];
    };

    expect(vm.errorMessage).toContain('Failed to load modules');
    expect(vm.modules).toHaveLength(0);
  });

  it('should reset form when resetForm is called', () => {
    const wrapper = mountComponent();

    const vm = wrapper.vm as {
      form: { moduleId: string; title: string; description: string; contactEmail: string; website: string };
      errors: Record<string, string>;
      successMessage: string;
      errorMessage: string;
      issueKey: string;
      issueUrl: string;
      resetForm: () => void;
    };

    // Set form values
    vm.form = {
      moduleId: 'nexus',
      title: 'Test',
      description: 'Test description',
      contactEmail: 'test@example.com',
      website: '',
    };
    vm.errors = { title: 'Some error' };
    vm.successMessage = 'Success!';
    vm.errorMessage = 'Error!';
    vm.issueKey = 'NEXUS-123';
    vm.issueUrl = 'https://example.com';

    // Reset form
    vm.resetForm();

    // Verify everything is reset
    expect(vm.form.moduleId).toBe('');
    expect(vm.form.title).toBe('');
    expect(vm.form.description).toBe('');
    expect(vm.form.contactEmail).toBe('');
    expect(vm.form.website).toBe('');
    expect(Object.keys(vm.errors)).toHaveLength(0);
    expect(vm.successMessage).toBe('');
    expect(vm.errorMessage).toBe('');
    expect(vm.issueKey).toBe('');
    expect(vm.issueUrl).toBe('');
  });

  it('should not close modal when submitting', () => {
    const wrapper = mountComponent();

    const vm = wrapper.vm as {
      isSubmitting: boolean;
      handleClose: () => void;
    };

    vm.isSubmitting = true;
    vm.handleClose();

    expect(wrapper.emitted('close')).toBeFalsy();
  });

  it('should close and reset form when handleClose is called while not submitting', () => {
    const wrapper = mountComponent();

    const vm = wrapper.vm as {
      form: { moduleId: string; title: string; description: string; contactEmail: string; website: string };
      isSubmitting: boolean;
      handleClose: () => void;
    };

    vm.form.title = 'Test';
    vm.isSubmitting = false;
    vm.handleClose();

    expect(wrapper.emitted('close')).toBeTruthy();
    expect(vm.form.title).toBe('');
  });
});
