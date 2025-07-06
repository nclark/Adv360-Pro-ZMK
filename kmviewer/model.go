package main

import (
	"image"
	"path/filepath"
	"strings"

	tea "github.com/charmbracelet/bubbletea"
)

// Model represents the application state
type Model struct {
	// Image management
	imageFiles    []string
	currentIndex  int
	images        map[string]image.Image // Cache for loaded images
	resizedImages map[string]image.Image // Cache for resized images

	// UI state
	termWidth  int
	termHeight int
	ready      bool
}

// NewModel creates a new model with the given image files
func NewModel(imageFiles []string) *Model {
	return &Model{
		imageFiles:    imageFiles,
		currentIndex:  0,
		images:        make(map[string]image.Image),
		resizedImages: make(map[string]image.Image),
		ready:         false,
	}
}

// Init initializes the model
func (m *Model) Init() tea.Cmd {
	return nil
}

// Update handles messages and updates the model
func (m *Model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		m.termWidth = msg.Width
		m.termHeight = msg.Height
		m.ready = true
		// Clear resized image cache when window size changes
		m.resizedImages = make(map[string]image.Image)
		return m, nil

	case tea.KeyMsg:
		switch msg.String() {
		case "q", "ctrl+c":
			return m, tea.Quit

		case "left", "h":
			if m.currentIndex > 0 {
				m.currentIndex--
			}
			// Return a command to clear and redraw for cleaner image switching
			return m, tea.ClearScreen

		case "right", "l", "tab":
			if m.currentIndex < len(m.imageFiles)-1 {
				m.currentIndex++
			}
			// Return a command to clear and redraw for cleaner image switching
			return m, tea.ClearScreen

		case "shift+tab":
			if m.currentIndex > 0 {
				m.currentIndex--
			}
			// Return a command to clear and redraw for cleaner image switching
			return m, tea.ClearScreen
		}
	}

	return m, nil
}

// View renders the UI
func (m *Model) View() string {
	if !m.ready {
		return "Initializing..."
	}

	return renderView(m)
}

// getCurrentImage returns the currently selected image file
func (m *Model) getCurrentImage() string {
	if len(m.imageFiles) == 0 {
		return ""
	}
	return m.imageFiles[m.currentIndex]
}

// getMenuItems returns the menu items for display
func (m *Model) getMenuItems() []MenuItem {
	items := make([]MenuItem, len(m.imageFiles))
	for i, file := range m.imageFiles {
		// Clean up filename: remove prefix before dash and .png suffix
		displayName := filepath.Base(file)
		
		// Remove everything before and including the last dash
		if dashIndex := strings.LastIndex(displayName, "-"); dashIndex != -1 {
			displayName = displayName[dashIndex+1:]
		}
		
		// Remove .png suffix
		displayName = strings.TrimSuffix(displayName, ".png")
		
		items[i] = MenuItem{
			Text:     displayName,
			Selected: i == m.currentIndex,
		}
	}
	return items
}

// MenuItem represents a menu item
type MenuItem struct {
	Text     string
	Selected bool
}