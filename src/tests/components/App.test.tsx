import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'

describe('Basic Test setup', () => {
  it('should render a simple div', () => {
    render(<div>Basma+ App</div>)
    expect(screen.getByText('Basma+ App')).toBeInTheDocument()
  })
})
