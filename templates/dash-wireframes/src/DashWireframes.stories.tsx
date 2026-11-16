import type { Meta, StoryObj } from '@storybook/react-vite';
import { HeadlineCards, StoryTable, Trends, ScopeSelector, ErrorState, FullDashboard } from './DashWireframes';

const meta: Meta = { title: 'Factory Dashboard' };
export default meta;
type Story = StoryObj;

export const Headlines: Story = { render: () => <HeadlineCards /> };
export const Table: Story = { render: () => <StoryTable /> };
export const TrendViews: Story = { render: () => <Trends /> };
export const Scope: Story = { render: () => <ScopeSelector /> };
export const ScopeEmpty: Story = { render: () => <ScopeSelector empty /> };
export const Error: Story = { render: () => <ErrorState /> };
export const Full: Story = { render: () => <FullDashboard /> };
