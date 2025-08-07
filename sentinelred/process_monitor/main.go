package main

import (
    "encoding/json"
    "net/http"
)

func main() {
    http.HandleFunc("/processes", processesHandler)
    http.HandleFunc("/alerts", alertsHandler)
    http.ListenAndServe(":8080", nil)
}

func processesHandler(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodGet {
        http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
        return
    }
    json.NewEncoder(w).Encode(map[string][]string{"processes": {}})
}

func alertsHandler(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodGet {
        http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
        return
    }
    json.NewEncoder(w).Encode(map[string][]string{"alerts": {}})
}
