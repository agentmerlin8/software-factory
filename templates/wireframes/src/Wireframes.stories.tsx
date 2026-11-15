import type { Meta, StoryObj } from '@storybook/react-vite';
import { AddTask, TaskList, ToggleTask, DeleteTask, FilterView } from './Wireframes';

const meta: Meta = { title: 'To-Do Wireframes' };
export default meta;
type Story = StoryObj;

export const Add: Story = { render: () => <AddTask /> };
export const List: Story = { render: () => <TaskList /> };
export const ListEmpty: Story = { render: () => <TaskList empty /> };
export const Toggle: Story = { render: () => <ToggleTask /> };
export const Delete: Story = { render: () => <DeleteTask /> };
export const Filter: Story = { render: () => <FilterView /> };
