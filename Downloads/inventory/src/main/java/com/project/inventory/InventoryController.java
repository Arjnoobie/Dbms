package com.project.inventory;

import org.springframework.web.bind.annotation.*;
import java.time.LocalDate;
import java.util.List;

@RestController
@CrossOrigin(origins = "*")
public class InventoryController {

    private final InventoryRepository inventoryRepository;
    private final SalesHistoryRepository salesHistoryRepository;

    public InventoryController(InventoryRepository inventoryRepository,
                               SalesHistoryRepository salesHistoryRepository) {
        this.inventoryRepository = inventoryRepository;
        this.salesHistoryRepository = salesHistoryRepository;
    }

    // Link to see all items
    @GetMapping("/api/items")
    public List<InventoryItem> getAllItems() {
        return inventoryRepository.findAll();
    }

    // Link to update stock (+1 or -1)
    @PostMapping("/api/items/{id}/update")
    public void updateStock(@PathVariable Long id, @RequestParam int change) {
        InventoryItem item = inventoryRepository.findById(id).orElseThrow();
        item.setCurrentStock(item.getCurrentStock() + change);
        inventoryRepository.save(item);
    }

    // Link to get last 30 days of sales data for the chart
    // Java calculates the date and passes it to the query (JPQL cannot do date arithmetic directly)
    @GetMapping("/api/sales")
    public List<SalesHistorySummary> getSales() {
        LocalDate startDate = LocalDate.now().minusDays(30);
        return salesHistoryRepository.getDailySalesLast30Days(startDate);
    }
}
