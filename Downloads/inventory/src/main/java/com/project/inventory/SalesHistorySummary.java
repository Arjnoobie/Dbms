package com.project.inventory;

import java.time.LocalDate;

public class SalesHistorySummary {
    public LocalDate saleDate;
    public Long totalQuantitySold;

    public SalesHistorySummary(LocalDate saleDate, Long totalQuantitySold) {
        this.saleDate = saleDate;
        this.totalQuantitySold = totalQuantitySold;
    }
}
