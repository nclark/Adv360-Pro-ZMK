package main

import (
	"fmt"
	"os"

	tea "github.com/charmbracelet/bubbletea"
)

func main() {
	// Validate command line arguments
	if len(os.Args) < 2 {
		fmt.Println("Usage: kmviewer <image1> <image2> ...")
		os.Exit(1)
	}

	// Get image file paths from command line arguments
	imageFiles := os.Args[1:]

	// Validate that all files exist and are readable
	for _, file := range imageFiles {
		if _, err := os.Stat(file); os.IsNotExist(err) {
			panic(fmt.Sprintf("Image file does not exist: %s", file))
		}
	}

	// Create initial model
	model := NewModel(imageFiles)

	// Create and run the Bubble Tea program
	program := tea.NewProgram(model, tea.WithAltScreen())
	if _, err := program.Run(); err != nil {
		panic(fmt.Sprintf("Error running program: %v", err))
	}
}