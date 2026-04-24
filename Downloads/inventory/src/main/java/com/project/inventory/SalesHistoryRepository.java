package com.project.inventory;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import java.time.LocalDate;
import java.util.List;

public interface SalesHistoryRepository extends JpaRepository<SalesHistory, Long> {

    @Query("SELECT new com.project.inventory.SalesHistorySummary(s.saleDate, SUM(s.quantitySold)) " +
           "FROM SalesHistory s " +
           "WHERE s.saleDate >= :startDate " +
           "GROUP BY s.saleDate ORDER BY s.saleDate")
    List<SalesHistorySummary> getDailySalesLast30Days(@Param("startDate") LocalDate startDate);
}
