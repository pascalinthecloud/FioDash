CREATE TABLE IF NOT EXISTS iops_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                hostname VARCHAR(255),
                read_iops FLOAT,
                write_iops FLOAT,
                cpu_usage FLOAT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
