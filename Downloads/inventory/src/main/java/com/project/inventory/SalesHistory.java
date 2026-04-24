package com.project.inventory;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDate;

@Entity
@Data
public class SalesHistory {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private Long itemId; // Matches your 'item_id' column
    private LocalDate saleDate; // Matches your 'sale_date' column
    private Integer quantitySold; // Matches your 'quantity_sold' column
}