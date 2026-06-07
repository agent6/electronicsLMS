module.exports = {
  content: ["./templates/**/*.html", "./**/*.py"],
  theme: {
    extend: {
      colors: {
        ink: "#061331",
        "ink-soft": "#31405e",
        muted: "#657493",
        line: "#d8e3f5",
        brand: {
          blue: "#0a68ff",
          deep: "#0546c7",
          cyan: "#16b7c8",
          mint: "#22b782",
          orange: "#f59d2a",
          red: "#f04a4a",
        },
      },
      borderRadius: {
        card: "1rem",
      },
      boxShadow: {
        soft: "0 14px 38px rgba(20, 54, 112, 0.10)",
        lift: "0 24px 70px rgba(16, 66, 148, 0.14)",
      },
    },
  },
  plugins: [require("@tailwindcss/forms")],
};
