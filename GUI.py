import FaceDrawingApp

if __name__ == "__main__":
    app = FaceDrawingApp.FaceDrawingApp()
    app.option_add("*Button.HighlightBackground", app.style_config['color_primary'])
    app.option_add("*Button.HighlightColor", "white")
    app.mainloop()
