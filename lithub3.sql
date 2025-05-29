-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 29, 2025 at 04:25 PM
-- Server version: 10.4.28-MariaDB
-- PHP Version: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `lithub3`
--

-- --------------------------------------------------------

--
-- Table structure for table `bank_accounts`
--

CREATE TABLE `bank_accounts` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `bank_name` varchar(100) NOT NULL,
  `account_number` varchar(50) NOT NULL,
  `account_holder` varchar(100) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `bank_details`
--

CREATE TABLE `bank_details` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `bank_name` varchar(255) NOT NULL,
  `account_number` varchar(255) NOT NULL,
  `account_holder` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `cart`
--

CREATE TABLE `cart` (
  `cart_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `cart`
--

INSERT INTO `cart` (`cart_id`, `user_id`, `product_id`, `quantity`) VALUES
(25, 7, 7, 1),
(56, 22, 7, 1),
(75, 23, 35, 1),
(76, 23, 34, 1),
(83, 24, 7, 1),
(93, 26, 35, 1);

-- --------------------------------------------------------

--
-- Table structure for table `chat_messages`
--

CREATE TABLE `chat_messages` (
  `message_id` int(11) NOT NULL,
  `sender_id` int(11) NOT NULL,
  `receiver_id` int(11) NOT NULL,
  `message` text NOT NULL,
  `timestamp` datetime DEFAULT current_timestamp(),
  `is_admin_reply` tinyint(1) DEFAULT 0,
  `status` varchar(20) DEFAULT 'unread',
  `reply_to_message_id` int(11) DEFAULT NULL,
  `is_reply` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `chat_messages`
--

INSERT INTO `chat_messages` (`message_id`, `sender_id`, `receiver_id`, `message`, `timestamp`, `is_admin_reply`, `status`, `reply_to_message_id`, `is_reply`) VALUES
(9, 1, 1, 'Inquiry about Order #43', '2024-12-01 13:06:07', 0, 'read', NULL, 0),
(12, 1, 1, 'Inquiry about Order #43', '2024-12-03 21:41:45', 0, 'read', NULL, 0),
(20, 1, 1, 'Inquiry about Order #43', '2024-12-04 19:14:30', 0, 'read', NULL, 0),
(26, 1, 1, 'Inquiry about Order #43 - Transformers One', '2024-12-05 18:59:34', 0, 'read', NULL, 0),
(27, 1, 1, 'Inquiry about Order #43 - Transformers One', '2024-12-05 19:01:35', 0, 'read', NULL, 0),
(28, 1, 1, 'Inquiry about Order #43 - Transformers One', '2024-12-05 19:02:10', 0, 'read', NULL, 0),
(29, 1, 1, 'Inquiry about Order #37 - Born Pink', '2024-12-05 19:06:08', 0, 'read', NULL, 0),
(30, 1, 1, 'Inquiry about Order #29 - It Ends with Us', '2024-12-05 19:09:34', 0, 'read', NULL, 0),
(31, 17, 1, 'Inquiry about Order #46 - Percy Jackson', '2024-12-05 19:58:36', 0, 'read', NULL, 0),
(36, 1, 17, 'inihahanda na ang iyong order', '2024-12-05 22:34:58', 0, 'read', NULL, 0),
(37, 17, 1, 'weh?', '2024-12-05 23:04:39', 0, 'read', NULL, 0),
(38, 17, 1, 'Inquiry about Order #46 - Percy Jackson', '2024-12-05 23:31:30', 0, 'read', NULL, 0),
(39, 17, 1, 'Inquiry about Order #46 - Percy Jackson', '2024-12-05 23:38:07', 0, 'read', NULL, 0),
(40, 17, 1, 'Inquiry about Order #46 - Percy Jackson', '2024-12-05 23:38:08', 0, 'read', NULL, 0),
(41, 17, 1, 'Inquiry about Order #46 - Percy Jackson', '2024-12-06 00:04:18', 0, 'read', NULL, 0),
(42, 17, 1, 'Inquiry about Order #46 - Percy Jackson', '2024-12-06 00:32:56', 0, 'read', NULL, 0),
(43, 1, 17, 'oo nga', '2024-12-06 10:39:23', 0, 'read', NULL, 0),
(44, 1, 1, 'Inquiry about Order #47 - Heroes of Olympus', '2024-12-08 12:18:32', 0, 'read', NULL, 0),
(45, 1, 1, 'Inquiry about Order #47 - Heroes of Olympus', '2024-12-08 12:23:12', 0, 'read', NULL, 0),
(46, 1, 1, 'Inquiry about Order #47 - Heroes of Olympus', '2024-12-08 12:23:15', 0, 'read', NULL, 0),
(47, 1, 1, 'Inquiry about Order #47 - Heroes of Olympus', '2024-12-08 12:52:06', 0, 'read', NULL, 0),
(48, 1, 19, 'Inquiry about Order #44 - Nokturno', '2024-12-08 12:53:24', 0, 'unread', NULL, 0),
(49, 1, 1, 'Inquiry about Order #45 - Forbes Magazine 2023', '2024-12-08 12:53:54', 0, 'read', NULL, 0),
(50, 1, 1, 'Inquiry about Order #47 - Heroes of Olympus', '2024-12-08 12:55:39', 0, 'read', NULL, 0),
(51, 1, 1, 'Inquiry about Order #45 - Forbes Magazine 2023', '2024-12-08 12:58:07', 0, 'read', NULL, 0),
(52, 1, 1, 'Inquiry about Order #32 - Clever Lands', '2024-12-08 13:03:13', 0, 'read', NULL, 0),
(53, 17, 1, 'Inquiry about Order #46 - Percy Jackson', '2024-12-10 17:38:04', 0, 'read', NULL, 0),
(54, 17, 1, 'Inquiry about Order #52 - It Ends with Us', '2024-12-13 09:20:55', 0, 'read', NULL, 0),
(55, 25, 1, 'Inquiry about Order #56 - Red Queen', '2024-12-13 10:54:14', 0, 'read', NULL, 0),
(56, 25, 1, 'asd', '2024-12-13 10:54:40', 0, 'read', NULL, 0);

-- --------------------------------------------------------

--
-- Table structure for table `chat_messages_backup`
--

CREATE TABLE `chat_messages_backup` (
  `message_id` int(11) NOT NULL,
  `sender_id` int(11) NOT NULL,
  `receiver_id` int(11) NOT NULL,
  `message` text NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `is_admin_reply` tinyint(1) DEFAULT 0,
  `status` enum('unread','read','replied') DEFAULT 'unread',
  `reply_to_message_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `chat_messages_backup`
--

INSERT INTO `chat_messages_backup` (`message_id`, `sender_id`, `receiver_id`, `message`, `created_at`, `is_admin_reply`, `status`, `reply_to_message_id`) VALUES
(0, 4, 1, 'secret', '2024-11-30 15:20:17', 1, 'unread', NULL),
(0, 1, 4, 'weh', '2024-11-30 20:01:13', 0, 'unread', NULL),
(0, 1, 4, 'haha', '2024-12-01 01:34:57', 0, 'unread', NULL),
(0, 1, 4, 'gsfd', '2024-12-01 01:52:54', 0, 'unread', NULL),
(0, 1, 4, 'cxcx', '2024-12-01 01:57:53', 0, 'unread', NULL),
(0, 1, 4, 'zxz', '2024-12-01 01:58:54', 0, 'unread', NULL),
(0, 1, 4, 'hh', '2024-12-01 02:04:22', 0, 'unread', NULL),
(0, 1, 4, 'dsd', '2024-12-01 02:06:21', 0, 'unread', NULL),
(0, 1, 4, 'hjhjh', '2024-12-01 02:07:04', 0, 'unread', NULL),
(0, 1, 4, 'cvc', '2024-12-01 02:15:53', 0, 'unread', NULL),
(0, 1, 4, 'cvzxcz', '2024-12-01 02:18:10', 0, 'unread', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `chat_message_status`
--

CREATE TABLE `chat_message_status` (
  `status_id` int(11) NOT NULL,
  `message_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `is_read` tinyint(1) DEFAULT 0,
  `last_read_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `chat_message_status`
--

INSERT INTO `chat_message_status` (`status_id`, `message_id`, `user_id`, `is_read`, `last_read_at`, `created_at`) VALUES
(0, 0, 1, 0, NULL, '2024-11-30 15:20:17'),
(0, 0, 4, 0, NULL, '2024-12-01 01:34:57'),
(0, 0, 4, 0, NULL, '2024-12-01 01:52:54'),
(0, 0, 4, 0, NULL, '2024-12-01 02:15:53'),
(0, 0, 4, 0, NULL, '2024-12-01 02:18:10'),
(0, 1, 1, 0, NULL, '2024-12-01 02:44:49'),
(0, 2, 4, 0, NULL, '2024-12-01 02:45:07'),
(0, 3, 4, 0, NULL, '2024-12-01 02:52:07'),
(0, 4, 4, 0, NULL, '2024-12-01 03:56:46'),
(0, 6, 4, 0, NULL, '2024-12-01 04:47:43'),
(0, 7, 4, 0, NULL, '2024-12-01 04:55:23'),
(0, 10, 4, 0, NULL, '2024-12-03 10:53:42'),
(0, 11, 1, 0, NULL, '2024-12-03 11:14:26'),
(0, 14, 1, 0, NULL, '2024-12-04 09:23:56'),
(0, 16, 1, 0, NULL, '2024-12-04 09:32:09'),
(0, 19, 1, 0, NULL, '2024-12-04 10:59:38'),
(0, 32, 1, 0, NULL, '2024-12-05 12:27:50'),
(0, 33, 1, 0, NULL, '2024-12-05 13:50:00');

-- --------------------------------------------------------

--
-- Table structure for table `chat_replies`
--

CREATE TABLE `chat_replies` (
  `reply_id` int(11) NOT NULL,
  `message_id` int(11) NOT NULL,
  `sender_id` int(11) NOT NULL,
  `reply_text` text NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `contact_messages`
--

CREATE TABLE `contact_messages` (
  `message_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `phone` varchar(255) DEFAULT NULL,
  `message` text DEFAULT NULL,
  `status` enum('pending','replied') DEFAULT 'pending',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `contact_messages`
--

INSERT INTO `contact_messages` (`message_id`, `user_id`, `name`, `email`, `phone`, `message`, `status`, `created_at`) VALUES
(0, 1, 'Joyce Ramos', 'joyceramos@gmail.com', '9053712734', 'kailan po sales?', 'replied', '2024-11-30 14:46:02'),
(0, 1, NULL, NULL, NULL, 'weh', 'replied', '2024-11-30 20:01:13'),
(0, 1, NULL, NULL, NULL, 'cxcx', 'replied', '2024-12-01 01:57:53'),
(0, 1, NULL, NULL, NULL, 'zxz', 'replied', '2024-12-01 01:58:54'),
(0, 1, 'Joyce Ramos', 'joyceramos@gmail.com', '9053712734', 'hghd', 'replied', '2024-12-01 02:03:19'),
(0, 1, NULL, NULL, NULL, 'hh', 'replied', '2024-12-01 02:04:22'),
(0, 1, 'Joyce Ramos', 'joyceramos@gmail.com', '9053712734', 'hello', 'replied', '2024-12-01 02:34:25'),
(0, 1, 'Joyce Ramos', 'joyceramos@gmail.com', '9053712734', 'Does the year end sale happening?', 'replied', '2024-12-03 11:12:40'),
(0, 17, 'Kikay Ramos', 'joyceramos270@gmail.com', '9165506792', 'Does the year end sale happening this year?', 'replied', '2024-12-05 11:59:24');

-- --------------------------------------------------------

--
-- Table structure for table `couriers`
--

CREATE TABLE `couriers` (
  `id` int(50) NOT NULL,
  `email` varchar(250) NOT NULL,
  `password` varchar(250) NOT NULL,
  `name` varchar(250) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `couriers`
--

INSERT INTO `couriers` (`id`, `email`, `password`, `name`) VALUES
(1, 'courier1@gmail.com', '123456', 'Courier');

-- --------------------------------------------------------

--
-- Table structure for table `favorites`
--

CREATE TABLE `favorites` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `favorites`
--

INSERT INTO `favorites` (`id`, `user_id`, `product_id`, `created_at`) VALUES
(2, 1, 9, '2024-10-30 12:50:29'),
(3, 1, 7, '2024-11-11 11:58:02'),
(4, 1, 20, '2024-11-12 01:30:46'),
(5, 1, 34, '2024-11-12 02:55:21'),
(6, 1, 6, '2024-11-12 03:16:45'),
(7, 19, 6, '2024-11-12 06:14:00'),
(8, 1, 24, '2024-11-30 13:47:35'),
(9, 1, 35, '2024-11-30 13:51:39'),
(11, 17, 6, '2024-12-10 10:34:06'),
(12, 17, 8, '2024-12-13 01:58:35');

-- --------------------------------------------------------

--
-- Table structure for table `inventory`
--

CREATE TABLE `inventory` (
  `inventory_id` int(11) NOT NULL,
  `product_id` int(11) DEFAULT NULL,
  `seller_id` int(11) DEFAULT NULL,
  `quantity` int(11) NOT NULL,
  `last_updated` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `message_replies`
--

CREATE TABLE `message_replies` (
  `reply_id` int(11) NOT NULL,
  `message_id` int(11) DEFAULT NULL,
  `admin_id` int(11) DEFAULT NULL,
  `reply_text` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

CREATE TABLE `notifications` (
  `notification_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `message` text NOT NULL,
  `type` varchar(50) DEFAULT 'general',
  `order_id` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `is_read` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `notifications`
--

INSERT INTO `notifications` (`notification_id`, `user_id`, `message`, `type`, `order_id`, `created_at`, `is_read`) VALUES
(138, 1, 'Welcome to LitHub! This is your notification center.', 'welcome', NULL, '2024-12-01 02:22:10', 1),
(140, 17, 'Your order is now being processed.', 'order_status', 46, '2024-12-08 18:54:13', 1),
(143, 1, 'Your order is now being processed.', 'order_status', 45, '2024-12-08 22:22:33', 1),
(144, 19, 'Your order is now being processed.', 'order_status', 41, '2024-12-08 22:22:48', 0),
(145, 1, 'Good news! Your order has been shipped.', 'order_status', 45, '2024-12-09 21:44:26', 1),
(148, 17, 'Dear Kikay Ramos,\nYour seller registration request has been declined for the following reason:\nincomplete_information\n\nAdditional Comments:\nxzx\n\nYou can submit a new application after 30 days with complete documentation.\nIf you have any questions, please contact our support team.', 'seller_request', NULL, '2024-12-10 18:33:15', 0),
(149, 17, 'Your order is now being processed.', 'order_status', 50, '2024-12-12 16:28:22', 0),
(150, 17, 'Your order has been cancelled by the seller.', 'order_status', 52, '2024-12-13 09:16:03', 1),
(159, 17, 'Your seller registration has been approved! You can now start selling.', 'seller_approval', NULL, '2024-12-13 11:02:48', 0),
(161, 1, 'Your order is now being processed.', 'order_status', 57, '2024-12-13 11:37:16', 0),
(162, 1, 'Good news! Your order has been shipped.', 'order_status', 57, '2024-12-13 11:37:30', 0),
(163, 1, 'Your order has been completed. Thank you for shopping!', 'order_status', 57, '2024-12-13 11:38:09', 0),
(164, 1, 'Your order has been completed. Thank you for shopping!', 'order_status', 57, '2024-12-13 11:38:46', 0),
(165, 1, 'Your order has been completed. Thank you for shopping!', 'order_status', 57, '2024-12-13 11:38:47', 0),
(166, 1, 'Your order is now being processed.', 'order_status', 84, '2025-05-24 09:30:00', 1),
(167, 1, 'Your order is now being processed.', 'order_status', 86, '2025-05-24 15:55:11', 0),
(168, 1, 'Good news! Your order has been shipped.', 'order_status', 86, '2025-05-24 15:55:33', 0),
(169, 1, 'Your order is now being processed.', 'order_status', 89, '2025-05-29 21:43:24', 0),
(170, 1, 'Good news! Your order has been shipped.', 'order_status', 89, '2025-05-29 21:43:33', 0),
(171, 1, 'Your order is now pending processing.', 'order_status', 89, '2025-05-29 21:44:37', 0),
(172, 1, 'Your order is now being processed.', 'order_status', 89, '2025-05-29 21:44:45', 0),
(173, 1, 'Good news! Your order has been shipped.', 'order_status', 89, '2025-05-29 21:44:55', 0);

-- --------------------------------------------------------

--
-- Table structure for table `orders`
--

CREATE TABLE `orders` (
  `order_id` int(11) NOT NULL,
  `buyer_id` int(11) DEFAULT NULL,
  `order_date` timestamp NOT NULL DEFAULT current_timestamp(),
  `status` enum('pending','processing','shipped','picked','in-transit','completed','cancelled','return') DEFAULT 'pending',
  `total_price` decimal(10,2) DEFAULT NULL,
  `shipping_address` text NOT NULL,
  `payment_method` enum('credit_card','paypal','cod') NOT NULL,
  `completed_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `courier_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `orders`
--

INSERT INTO `orders` (`order_id`, `buyer_id`, `order_date`, `status`, `total_price`, `shipping_address`, `payment_method`, `completed_at`, `updated_at`, `courier_id`) VALUES
(1, 1, '2024-10-22 14:44:03', 'completed', 3600.00, 'Purok 1 Brgy. Balanac, magdalena, laguna, Philippines, 4007', 'cod', NULL, '2024-11-11 08:42:08', NULL),
(2, 1, '2024-10-23 08:35:36', 'pending', 900.00, 'balanac, magdalena, laguna, Philippines, 4007', 'cod', NULL, '2024-11-11 08:40:25', NULL),
(5, 1, '2024-10-28 08:27:04', 'completed', 450.00, 'barangay balanac, magdalena, laguna, Philippines, 4007', 'cod', NULL, '2024-11-11 08:48:57', NULL),
(7, 1, '2024-10-29 12:32:45', 'pending', NULL, 'barangay balanac, magdalena, laguna, Philippines, 4007', 'cod', NULL, '2024-11-11 08:40:25', NULL),
(8, 1, '2024-10-29 12:56:06', 'completed', 1350.00, 'barangay balanac, magdalena, laguna, Philippines, 4007', 'cod', NULL, '2024-11-11 09:00:09', NULL),
(9, 5, '2024-11-04 01:58:12', 'shipped', 450.00, 'brgy dos, sta cruz, laguna, Philippines, 4009', 'cod', NULL, '2024-11-11 23:56:05', NULL),
(10, 1, '2024-11-04 11:38:42', 'completed', 1800.00, 'purok 1 B, Balanac, Magdalena, Laguna, Philippines, 4007', 'cod', NULL, '2024-11-12 02:56:56', NULL),
(12, 1, '2024-11-08 07:16:27', 'completed', 1350.00, 'purok 1 B, Balanac, Magdalena, Laguna, Philippines, 4007', 'cod', NULL, '2024-11-12 03:09:05', NULL),
(13, 1, '2024-11-09 14:35:58', 'completed', 1350.00, 'purok 1 B, Balanac, Magdalena, Laguna, Philippines, 4007', 'cod', NULL, '2024-11-12 04:56:39', NULL),
(14, 1, '2024-11-09 20:54:32', 'processing', 450.00, 'purok 1 B, Balanac, Magdalena, Laguna, Philippines, 4007', 'cod', NULL, '2024-11-12 03:07:08', NULL),
(15, 1, '2024-11-11 12:24:00', 'completed', 900.00, 'purok 1 B, Balanac, Magdalena, Laguna, Philippines, 4007', 'cod', NULL, '2024-11-12 03:08:59', NULL),
(16, 1, '2024-11-11 12:27:54', 'pending', 0.00, 'purok 1 B, Balanac, Magdalena, Laguna, Philippines, 4007', 'cod', NULL, '2024-11-11 12:27:54', NULL),
(17, 1, '2024-11-11 12:29:18', 'pending', 0.00, 'purok 1 B, Balanac, Magdalena, Laguna, Philippines, 4007', 'cod', NULL, '2024-11-11 12:29:18', NULL),
(18, 1, '2024-11-11 12:30:31', 'pending', 0.00, 'purok 1 B, Balanac, Magdalena, Laguna, Philippines, 4007', 'cod', NULL, '2024-11-11 12:30:31', NULL),
(19, 1, '2024-11-11 12:32:30', 'pending', 0.00, 'purok 1 B, Balanac, Magdalena, Laguna, Philippines, 4007', 'cod', NULL, '2024-11-11 12:32:30', NULL),
(20, 1, '2024-11-11 12:34:14', 'pending', 0.00, 'purok 1 B, Balanac, Magdalena, Laguna, Philippines, 4007', 'cod', NULL, '2024-11-11 12:34:14', NULL),
(21, 1, '2024-11-11 12:37:12', 'pending', 0.00, 'purok 1 B, Balanac, Magdalena, Laguna, Philippines, 4007', 'cod', NULL, '2024-11-11 12:37:12', NULL),
(22, 1, '2024-11-11 12:44:10', 'pending', 0.00, 'purok 1 B, Balanac, Magdalena, Laguna, Philippines, 4007', 'cod', NULL, '2024-11-11 12:44:10', NULL),
(23, 1, '2024-11-11 12:45:38', 'pending', 0.00, 'purok 1 B, Balanac, Magdalena, Laguna, Philippines, 4007', 'cod', NULL, '2024-11-11 12:45:38', NULL),
(24, 1, '2024-11-11 12:47:26', 'pending', 0.00, 'purok 1 B, Balanac, Magdalena, Laguna, Philippines, 4007', 'cod', NULL, '2024-11-11 12:47:26', NULL),
(25, 1, '2024-11-11 13:05:08', 'completed', 900.00, 'purok 1 B, Balanac, Magdalena, Laguna, Philippines, 4007', 'cod', NULL, '2024-11-12 03:09:14', NULL),
(26, 1, '2024-11-11 13:08:23', 'completed', 900.00, 'purok 1 B, Balanac, Magdalena, Laguna, Philippines, 4007', 'cod', NULL, '2024-11-12 03:09:18', NULL),
(27, 19, '2024-11-11 23:50:03', 'completed', 450.00, 'palasan, Balanac, Magdalena, Laguna, 4009', 'cod', NULL, '2024-11-12 00:00:38', NULL),
(28, 19, '2024-11-11 23:54:44', 'picked', 450.00, 'palasan, Balanac, Magdalena, Laguna, 4009', 'cod', NULL, '2025-05-24 06:13:01', NULL),
(29, 1, '2024-11-12 01:42:56', 'completed', 450.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2024-11-12 03:08:50', NULL),
(30, 1, '2024-11-12 02:55:58', 'completed', 850.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2024-11-12 03:08:44', NULL),
(31, 1, '2024-11-12 03:26:09', 'completed', 675.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2024-11-12 03:27:11', NULL),
(32, 1, '2024-11-12 03:31:08', 'completed', 450.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2024-11-12 03:31:31', NULL),
(33, 1, '2024-11-12 03:40:44', 'completed', 450.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2024-11-12 03:44:59', NULL),
(34, 1, '2024-11-12 03:53:55', 'completed', 810.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2024-11-12 03:54:22', NULL),
(35, 1, '2024-11-12 04:01:45', 'completed', 450.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2024-11-12 04:03:56', NULL),
(36, 1, '2024-11-12 04:07:36', 'completed', 765.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2024-11-12 04:08:18', NULL),
(37, 1, '2024-11-12 04:08:45', 'completed', 850.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2024-11-12 04:15:09', NULL),
(38, 1, '2024-11-12 04:53:51', 'completed', 765.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2025-05-24 06:12:33', NULL),
(39, 19, '2024-11-14 05:54:47', 'cancelled', 810.00, 'palasan, Balanac, Magdalena, Laguna, 4009', 'cod', NULL, '2024-11-30 07:55:44', NULL),
(40, 19, '2024-11-14 05:56:05', 'completed', 566.00, 'palasan, Balanac, Magdalena, Laguna, 4009', 'cod', NULL, '2024-11-14 05:56:30', NULL),
(41, 19, '2024-11-15 04:00:37', 'processing', 450.00, 'palasan, Balanac, Magdalena, Laguna, 4009', 'cod', NULL, '2024-12-08 14:22:48', NULL),
(42, 1, '2024-11-27 14:15:18', 'pending', 566.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2024-11-27 14:15:18', NULL),
(43, 1, '2024-11-30 07:14:30', 'completed', 675.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2024-12-01 01:46:45', NULL),
(44, 1, '2024-11-30 11:03:37', 'pending', 450.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2024-11-30 11:03:37', NULL),
(45, 1, '2024-12-03 12:38:53', 'completed', 810.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2025-05-24 05:55:07', NULL),
(46, 17, '2024-12-05 11:55:55', 'processing', 450.00, 'purok1b, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2024-12-08 10:54:13', NULL),
(47, 1, '2024-12-06 04:16:02', 'completed', 450.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2025-05-24 05:52:30', NULL),
(48, 17, '2024-12-11 10:20:07', 'pending', 450.00, 'purok1b, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2024-12-11 10:20:07', NULL),
(49, 17, '2024-12-11 10:20:42', 'pending', 450.00, 'purok1b, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2024-12-11 10:20:42', NULL),
(50, 17, '2024-12-11 10:49:12', 'processing', 450.00, 'purok1b, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2024-12-12 08:28:22', NULL),
(51, 24, '2024-12-12 23:31:20', 'pending', 450.00, 'ville, Bagumbayan, Santa Cruz, Laguna, 4009', 'cod', NULL, '2024-12-12 23:31:20', NULL),
(52, 17, '2024-12-12 23:42:24', 'cancelled', 450.00, 'purok1b, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2024-12-13 01:16:03', NULL),
(53, 17, '2024-12-13 01:52:44', 'pending', 1620.00, 'purok1b, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2024-12-13 01:52:44', NULL),
(54, 17, '2024-12-13 01:53:17', 'pending', 1350.00, 'purok1b, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2024-12-13 01:53:17', NULL),
(56, 25, '2024-12-13 02:53:32', 'pending', 19350.00, 'asdasdasd, San Antonio, Kalayaan, Laguna, 4015', 'cod', NULL, '2024-12-13 02:53:32', NULL),
(57, 1, '2024-12-13 03:35:13', 'completed', 18450.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2024-12-13 03:38:09', NULL),
(59, 1, '2024-12-27 14:01:02', 'pending', 450.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2024-12-27 14:01:02', NULL),
(60, 1, '2024-12-27 14:05:34', 'pending', 810.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2024-12-27 14:05:34', NULL),
(61, 1, '2024-12-27 14:07:56', 'pending', 450.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2024-12-27 14:07:56', NULL),
(62, 1, '2024-12-27 14:20:10', 'pending', 810.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2024-12-27 14:20:10', NULL),
(63, 1, '2024-12-27 14:25:26', 'pending', 450.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2024-12-27 14:25:26', NULL),
(64, 1, '2024-12-27 14:32:36', 'pending', 566.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2024-12-27 14:32:36', NULL),
(65, 1, '2024-12-27 14:36:13', 'pending', 450.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2024-12-27 14:36:13', NULL),
(66, 1, '2024-12-27 14:39:54', 'pending', 450.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2024-12-27 14:39:54', NULL),
(67, 1, '2025-01-02 13:17:55', 'pending', 450.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2025-01-02 13:17:55', NULL),
(68, 1, '2025-02-12 11:59:03', 'pending', 450.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2025-02-12 11:59:03', NULL),
(69, 1, '2025-02-12 12:03:26', 'pending', 450.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2025-02-12 12:03:26', NULL),
(70, 1, '2025-02-21 02:42:06', 'pending', 850.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2025-02-21 02:42:06', NULL),
(71, 1, '2025-05-22 11:13:44', 'pending', 566.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', '', NULL, '2025-05-22 11:13:44', NULL),
(72, 1, '2025-05-22 11:18:34', 'pending', 810.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', '', NULL, '2025-05-22 11:18:34', NULL),
(73, 1, '2025-05-22 12:08:26', 'pending', 450.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', 'cod', NULL, '2025-05-22 12:08:26', NULL),
(75, 1, '2025-05-22 15:17:50', 'pending', 450.00, '', 'cod', NULL, '2025-05-22 15:17:50', NULL),
(76, 1, '2025-05-22 15:18:19', 'pending', 450.00, '', 'cod', NULL, '2025-05-22 15:18:19', NULL),
(77, 1, '2025-05-22 15:18:40', 'pending', 450.00, '', 'cod', NULL, '2025-05-22 15:18:40', NULL),
(78, 1, '2025-05-22 15:18:58', 'pending', 450.00, '', 'cod', NULL, '2025-05-22 15:18:58', NULL),
(79, 1, '2025-05-22 15:19:11', 'pending', 450.00, '', 'cod', NULL, '2025-05-22 15:19:11', NULL),
(80, 1, '2025-05-22 15:34:02', 'pending', 765.00, '', 'cod', NULL, '2025-05-22 15:34:02', NULL),
(81, 1, '2025-05-22 15:37:07', 'pending', 765.00, '', 'cod', NULL, '2025-05-22 15:37:07', NULL),
(82, 1, '2025-05-22 15:41:53', 'pending', 450.00, '', 'cod', NULL, '2025-05-22 15:41:53', NULL),
(83, 1, '2025-05-22 15:45:59', 'pending', 450.00, '', 'cod', NULL, '2025-05-22 15:45:59', NULL),
(84, 1, '2025-05-23 15:24:47', 'processing', 765.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', '', NULL, '2025-05-24 01:30:00', NULL),
(85, 1, '2025-05-24 06:49:08', 'completed', 450.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', '', NULL, '2025-05-24 06:53:29', NULL),
(86, 1, '2025-05-24 07:53:42', 'completed', 2250.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', '', NULL, '2025-05-24 08:01:08', NULL),
(87, 1, '2025-05-29 12:40:43', 'pending', 450.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', '', NULL, '2025-05-29 12:40:43', NULL),
(88, 1, '2025-05-29 13:28:54', 'pending', 450.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', '', NULL, '2025-05-29 13:28:54', NULL),
(89, 1, '2025-05-29 13:41:59', 'shipped', 450.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', '', NULL, '2025-05-29 13:44:55', NULL),
(90, 1, '2025-05-29 13:46:29', 'pending', 450.00, 'purok 1 B, Balanac, Magdalena, Laguna, 4007', '', NULL, '2025-05-29 13:46:29', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `order_items`
--

CREATE TABLE `order_items` (
  `order_item_id` int(11) NOT NULL,
  `order_id` int(11) DEFAULT NULL,
  `product_id` int(11) DEFAULT NULL,
  `quantity` int(11) NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `is_rated` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `order_items`
--

INSERT INTO `order_items` (`order_item_id`, `order_id`, `product_id`, `quantity`, `price`, `is_rated`) VALUES
(1, 1, 6, 7, 450.00, 0),
(2, 1, 9, 1, 450.00, 0),
(7, 5, 8, 1, 450.00, 0),
(9, 8, 8, 1, 450.00, 0),
(10, 8, 9, 1, 900.00, 0),
(11, 9, 7, 1, 450.00, 0),
(12, 10, 7, 1, 450.00, 0),
(13, 10, 6, 1, 900.00, 0),
(14, 10, 12, 1, 450.00, 0),
(17, 12, 7, 3, 450.00, 0),
(18, 13, 6, 1, 900.00, 0),
(19, 13, 12, 1, 450.00, 0),
(21, 14, 7, 1, 450.00, 0),
(22, 15, 6, 1, 450.00, 0),
(23, 15, 7, 1, 450.00, 0),
(25, 25, 6, 1, 450.00, 0),
(26, 25, 7, 1, 450.00, 0),
(28, 26, 6, 1, 450.00, 0),
(29, 26, 7, 1, 450.00, 0),
(31, 27, 7, 1, 450.00, 0),
(32, 28, 6, 1, 450.00, 0),
(33, 29, 24, 1, 450.00, 0),
(34, 30, 34, 1, 850.00, 0),
(35, 31, 25, 1, 675.00, 0),
(36, 32, 8, 1, 450.00, 0),
(37, 33, 9, 1, 450.00, 0),
(38, 34, 35, 1, 810.00, 0),
(39, 35, 7, 1, 450.00, 0),
(40, 36, 33, 1, 765.00, 0),
(41, 37, 34, 1, 850.00, 0),
(42, 38, 33, 1, 765.00, 0),
(43, 39, 35, 1, 810.00, 0),
(44, 40, 26, 1, 566.00, 0),
(45, 41, 7, 1, 450.00, 0),
(46, 42, 26, 1, 566.00, 0),
(47, 43, 25, 1, 675.00, 0),
(48, 44, 31, 1, 450.00, 0),
(49, 45, 35, 1, 810.00, 0),
(50, 46, 20, 1, 450.00, 0),
(51, 47, 9, 1, 450.00, 0),
(52, 48, 8, 1, 450.00, 0),
(53, 49, 9, 1, 450.00, 0),
(54, 50, 12, 1, 450.00, 0),
(55, 51, 6, 1, 450.00, 0),
(56, 52, 24, 1, 450.00, 0),
(57, 53, 35, 2, 810.00, 0),
(58, 54, 7, 1, 450.00, 0),
(59, 54, 20, 2, 450.00, 0),
(60, 56, 6, 43, 450.00, 0),
(61, 57, 7, 41, 450.00, 0),
(62, 59, 8, 1, 450.00, 0),
(63, 60, 35, 1, 810.00, 0),
(64, 61, 24, 1, 450.00, 0),
(65, 62, 35, 1, 810.00, 0),
(66, 63, 20, 1, 450.00, 0),
(67, 64, 26, 1, 566.00, 0),
(68, 65, 12, 1, 450.00, 0),
(69, 66, 20, 1, 450.00, 0),
(70, 67, 7, 1, 450.00, 0),
(71, 68, 7, 1, 450.00, 0),
(72, 69, 9, 1, 450.00, 0),
(73, 70, 34, 1, 850.00, 0),
(74, 71, 26, 1, 566.00, 0),
(75, 72, 35, 1, 810.00, 0),
(76, 73, 8, 1, 450.00, 0),
(78, 75, 7, 1, 450.00, 0),
(79, 76, 7, 1, 450.00, 0),
(80, 77, 7, 1, 450.00, 0),
(81, 78, 7, 1, 450.00, 0),
(82, 79, 7, 1, 450.00, 0),
(83, 80, 33, 1, 765.00, 0),
(84, 81, 33, 1, 765.00, 0),
(85, 82, 8, 1, 450.00, 0),
(86, 83, 12, 1, 450.00, 0),
(87, 84, 33, 1, 765.00, 0),
(88, 85, 20, 1, 450.00, 0),
(89, 86, 7, 5, 450.00, 0),
(90, 87, 9, 1, 450.00, 0),
(91, 88, 12, 1, 450.00, 0),
(92, 89, 12, 1, 450.00, 0),
(93, 90, 12, 1, 450.00, 0);

-- --------------------------------------------------------

--
-- Table structure for table `payments`
--

CREATE TABLE `payments` (
  `payment_id` int(11) NOT NULL,
  `order_id` int(11) DEFAULT NULL,
  `payment_date` timestamp NOT NULL DEFAULT current_timestamp(),
  `amount` decimal(10,2) NOT NULL,
  `payment_method` enum('credit_card','paypal','cod') NOT NULL,
  `payment_status` enum('completed','failed','pending') DEFAULT 'pending'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `payment_methods`
--

CREATE TABLE `payment_methods` (
  `payment_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `card_name` varchar(255) NOT NULL,
  `last_four` varchar(4) NOT NULL,
  `exp_month` varchar(2) NOT NULL,
  `exp_year` varchar(4) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `products`
--

CREATE TABLE `products` (
  `product_id` int(11) NOT NULL,
  `seller_id` int(11) DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `author` varchar(255) NOT NULL,
  `category` varchar(155) NOT NULL,
  `description` text DEFAULT NULL,
  `original_price` decimal(20,0) NOT NULL,
  `discount_percentage` int(11) NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `quantity` int(11) NOT NULL,
  `image` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `status` enum('available','out of stock','discontinued') DEFAULT 'available',
  `average_rating` decimal(2,1) DEFAULT 0.0,
  `rating_count` int(11) DEFAULT 0,
  `likes_count` int(11) DEFAULT 0,
  `genre` varchar(255) NOT NULL,
  `is_promo` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `products`
--

INSERT INTO `products` (`product_id`, `seller_id`, `name`, `author`, `category`, `description`, `original_price`, `discount_percentage`, `price`, `quantity`, `image`, `created_at`, `status`, `average_rating`, `rating_count`, `likes_count`, `genre`, `is_promo`) VALUES
(6, 1, 'Red Queen', 'Victoria Aveyard', 'Fiction & Non-Fiction Books', 'This a world divided by blood-red or silver. The Reds are commoners, ruled by a Silver elite in possession of God-like superpowers. ', 900, 50, 450.00, 0, 'book-4.jpg', '2024-10-14 12:22:00', 'available', 0.0, 0, 0, 'Fantasy', 0),
(7, 1, 'Wright Brothers', 'David McCullough', 'Fiction & Non-Fiction Books', 'A story about two brothers and one incredible moment in American history.', 900, 50, 450.00, 0, 'book-2.jpg', '2024-10-15 12:59:03', 'available', 0.0, 0, 0, 'Biography', 0),
(8, 1, 'Clever Lands', 'Rick Roldan', 'Fiction & Non-Fiction Books', 'yuiagaiduashsdalsjdh', 900, 50, 450.00, 8, 'book-11.jpg', '2024-10-16 05:17:52', 'available', 0.0, 0, 0, 'Romance', 0),
(9, 1, 'Heroes of Olympus', 'Rick Riordan', 'Fiction & Non-Fiction Books', 'Fight the giants to prove to the other Gods that they are worthy to fight alongside the Gods', 900, 50, 450.00, 48, '1368051707-2.jpg', '2024-10-16 05:46:39', 'available', 0.0, 0, 0, 'Science Fiction', 1),
(12, 1, 'Harry Potter', 'Eran Creevy, Joe Pearlman,', 'Fiction & Non-Fiction Books', 'Cast and crew reunite to celebrate the fantastical, magical world of Hogwarts on the 20th anniversary of the franchise\'s first film, \'Harry Potter and the Philosopher\'s Stone\'.', 900, 50, 450.00, 40, 'IMG_5466.JPG', '2024-10-17 14:53:12', 'available', 0.0, 0, 0, 'Fantasy', 1),
(20, 1, 'Percy Jackson', 'Rick Riordan', 'Fiction & Non-Fiction Books', 'Percy Jackson is the eponymous hero of the best selling Percy Jackson and the Olympian series  by Rick Riordan. He made his debut in the Lighting Thief at just 12 years old, where he discovered the shocking truth about his parentage: He is a demigod, the son of a mortal woman and the god Poseidon.', 900, 50, 450.00, 10, 'book-10.jpg', '2024-11-04 10:47:38', 'available', 0.0, 0, 0, 'Fantasy', 0),
(24, 1, 'It Ends with Us', 'It Ends with Us', 'Movie DVDs & Blu-ray', 'Lily Bloom moves to Boston to chase her lifelong dream of opening her own business. A chance meeting with charming neurosurgeon Ryle Kincaid soon sparks an intense connection, but as the two fall deeply in love, she begins to see sides of Ryle that remind her of her parents\' relationship. When Lily\'s first love, Atlas Corrigan, suddenly reenters her life, her relationship with Ryle gets upended, leaving her with an impossible choice.', 900, 50, 450.00, 51, 'IMG_5465.JPG', '2024-11-11 09:05:54', 'available', 0.0, 0, 0, 'Romance', 0),
(25, 1, 'Transformers One', 'Josh Cooley', 'Movie DVDs & Blu-ray', 'Optimus Prime and Megatron, as former friends, bonded like brothers. Their relationship ultimately changes Cybertron\'s fate forever.', 900, 25, 675.00, 4, 'IMG_5463.JPG', '2024-11-11 13:14:05', 'available', 0.0, 0, 0, 'Sci-Fi', 0),
(26, 19, 'The HAHA', 'omar', 'Magazines & Periodicals', 'basta', 566, 0, 566.00, 28, '1f4ab313-bb02-4009-8893-cabfbdc68c6b.jpg', '2024-11-11 16:17:12', 'available', 0.0, 0, 0, 'Lifestyle', 0),
(31, 19, 'Nokturno', 'Mikhail Red', 'Movie DVDs & Blu-ray', 'Jamie, an overseas worker, returns to her home province after her sister is mysteriously killed. She soon discovers that their family is cursed, and she must face her tragic past to save her soul from the mysterious entity known as the Kumakatok.', 900, 50, 450.00, 69, 'IMG_5464.JPG', '2024-11-12 00:25:21', 'available', 0.0, 0, 0, 'Horror', 1),
(32, 19, 'It Ends with Us', 'Justin Baldoni', 'Movie DVDs & Blu-ray', 'Lily Bloom moves to Boston to chase her lifelong dream of opening her own business. A chance meeting with charming neurosurgeon Ryle Kincaid soon sparks an intense connection, but as the two fall deeply in love, she begins to see sides of Ryle that remind her of her parents\' relationship. When Lily\'s first love, Atlas Corrigan, suddenly reenters her life, her relationship with Ryle gets upended, leaving her with an impossible choice.', 900, 50, 450.00, 15, 'IMG_5465.JPG', '2024-11-12 00:28:52', 'available', 0.0, 0, 0, 'Romance', 0),
(33, 1, 'Talaarawan', 'BINI', 'Music CDs & Vinyl Records', 'P-pop phenomenons BINI have just released their first ever extended-play, titled “Talaarawan”. The highly-anticipated record features the hit tracks “Karera” and “Pantropiko“, as well as four new tracks –– including the EP’s lead single “Salamin, Salamin“.', 900, 15, 765.00, 16, 'IMG_5467.JPG', '2024-11-12 01:09:19', 'available', 0.0, 0, 0, 'Pop', 0),
(34, 1, 'Born Pink', 'BLACK PINK', 'Music CDs & Vinyl Records', 'Born Pink is the second studio album by South Korean girl group Blackpink. It was released on September 16, 2022, through YG Entertainment and Interscope Records. It marked the group\'s first full-length record since The Album in 2020.', 1000, 15, 850.00, 0, 'IMG_5471.JPG', '2024-11-12 01:11:06', 'available', 0.0, 0, 0, 'Pop', 0),
(35, 1, 'Forbes Magazine 2023', 'Forbes', 'Magazines & Periodicals', ': Forbes brings you the authoritative information you need to be financially successful. Every issue of Forbes is packed with all the critical news and information you need about business, money and investing, market trends, technology, portfolio strategies and much more. Achieve your business and financial goals with the coverage found only in Forbes!', 900, 10, 810.00, 41, 'IMG_5477.JPG', '2024-11-12 01:13:18', 'available', 0.0, 0, 0, 'Business', 0);

-- --------------------------------------------------------

--
-- Table structure for table `related_products`
--

CREATE TABLE `related_products` (
  `product_id` int(11) NOT NULL,
  `related_product_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `reviews`
--

CREATE TABLE `reviews` (
  `review_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `buyer_id` int(11) NOT NULL,
  `product_quality` int(11) NOT NULL,
  `seller_service` int(11) NOT NULL,
  `delivery_service` int(11) NOT NULL,
  `quality_comment` text DEFAULT NULL,
  `service_comment` text DEFAULT NULL,
  `delivery_comment` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `reviews`
--

INSERT INTO `reviews` (`review_id`, `product_id`, `buyer_id`, `product_quality`, `seller_service`, `delivery_service`, `quality_comment`, `service_comment`, `delivery_comment`, `created_at`) VALUES
(4, 34, 1, 5, 5, 5, 'cvcv', 'cvcv', 'cxvxcv', '2024-11-30 06:09:19'),
(5, 33, 1, 5, 4, 5, 'cc', 'zczxcz', 'ccf', '2024-11-30 06:18:34'),
(6, 7, 1, 4, 4, 5, 'bbcxv', 'vvcxb', 'vbcxvb', '2024-11-30 06:21:13'),
(7, 9, 1, 5, 5, 5, '', '', '', '2024-11-30 07:09:01'),
(8, 25, 1, 5, 5, 5, 'sddas', 'sds', 'sdasdas', '2024-12-01 01:47:00');

-- --------------------------------------------------------

--
-- Table structure for table `seller_requests`
--

CREATE TABLE `seller_requests` (
  `request_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `status` enum('pending','approved','rejected') DEFAULT 'pending',
  `request_date` timestamp NOT NULL DEFAULT current_timestamp(),
  `processed_date` timestamp NULL DEFAULT NULL,
  `rejection_reason` text DEFAULT NULL,
  `additional_comments` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `seller_requests`
--

INSERT INTO `seller_requests` (`request_id`, `user_id`, `status`, `request_date`, `processed_date`, `rejection_reason`, `additional_comments`) VALUES
(1, 1, 'approved', '2024-10-25 16:44:40', NULL, NULL, NULL),
(11, 5, 'approved', '2024-11-04 02:09:23', '2024-11-04 02:09:56', NULL, NULL),
(12, 19, 'approved', '2024-11-11 15:39:47', '2024-11-11 15:40:42', NULL, NULL),
(15, 17, 'rejected', '2024-12-10 07:29:34', '2024-12-10 10:33:15', 'incomplete_information', 'xzx'),
(17, 17, 'approved', '2024-12-13 02:59:07', NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `status` enum('active','inactive','banned') DEFAULT 'active',
  `is_seller` tinyint(1) DEFAULT 0,
  `profile_picture` varchar(255) NOT NULL,
  `is_admin` tinyint(1) DEFAULT 0,
  `gender` varchar(1) DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  `reset_token` varchar(6) DEFAULT NULL,
  `reset_token_expiry` datetime DEFAULT NULL,
  `is_verified` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `name`, `email`, `password`, `created_at`, `status`, `is_seller`, `profile_picture`, `is_admin`, `gender`, `date_of_birth`, `reset_token`, `reset_token_expiry`, `is_verified`) VALUES
(1, 'Joyce Ramos', 'joyceramos@gmail.com', 'scrypt:32768:8:1$6Mh6rRGcXXX4BBkJ$fbda58749725942500aaaeee70d165a32346c9851973e824354bbc96ba1feb858a189f7e676aa1736853bab1e4aedd6935e6f4517cd5fc4e66c2e8882d3a256e', '2024-10-11 12:41:20', 'active', 1, '20241127_222551_265349824_1592254661109534_235082275871300052_n.jpg', 0, 'F', '2004-03-05', NULL, NULL, 0),
(4, 'LitHub Admin', 'lithub_admin@gmail.com', 'pbkdf2:sha256:600000$AdQJxeBptkcNSGqD$a3358291e2310a90ef826a5d84de86c2043d5233240f518033f00f71c6dfed10', '2024-10-31 09:32:28', 'active', 0, '', 1, NULL, NULL, NULL, NULL, 0),
(5, 'Marc Leo', 'marcoleo@gmail.com', 'pbkdf2:sha256:600000$MmUfAbX1gCKfLpkA$ee4703501e407d80cedcf535672c84939bf645e48b0394d036cae99a0b5e47c9', '2024-11-04 01:56:05', 'active', 1, '40d935c9-ab88-483f-a62c-7f5e2c76d38b.jpg', 0, NULL, NULL, NULL, NULL, 0),
(6, 'Maxine Robles', 'max@gmail.com', 'pbkdf2:sha256:600000$n5ojjijWK5ftjgM4$ceaa5b4d4447a3976635af9302d66583cedf7fc86ad8fcaf8fb08ff557546ae2', '2024-11-08 07:10:34', 'active', 0, '', 0, NULL, NULL, NULL, NULL, 0),
(7, 'Rojean Malibiran', 'rojean@gmail.com', 'pbkdf2:sha256:600000$0ptaRn6FRbQpkzxw$bf2bac2869bd95f399db7a335e2e5c08b538e2952b4d6063fb577ed7a19b59b9', '2024-11-09 22:13:23', 'active', 0, '', 0, NULL, NULL, NULL, NULL, 0),
(17, 'Kikay Ramos', 'joyceramos270@gmail.com', 'scrypt:32768:8:1$di0iPtDtffeyKXi8$ed772d6d152ab8f16b40aeb7a751ec9369aae5880725b2a34c5e7afa17e538c04f95b3d1483cebdc649faf22ad6c85417fc414bbfe7b1bc8954c7e7094415709', '2024-11-11 11:23:27', 'active', 1, '20241111_194824_8591e73c-73e5-4419-b316-1a368c06dff6.jpg', 0, NULL, NULL, NULL, NULL, 0),
(18, 'Jannet Ramos', 'yanieclaricia@gmail.com', 'scrypt:32768:8:1$mcnzuaaJLQex4mhm$ee82fbf06a258aac88357735726d03941f8dc06c2f3c9caa8a848c34f34f950f9ea692f6c443c44da14862bd6b884237f409d5645ca22173fbd00287fb031b53', '2024-11-11 13:45:43', 'active', 0, '', 0, NULL, NULL, NULL, NULL, 0),
(19, 'leo', 'mleomapanao@gmail.com', 'scrypt:32768:8:1$P71yViSZW5KkW9h8$67152896b5efa701160ae9d95321804e53fe69b02062850d2324b3c002f4b4f5a905ecf4716c21ec89686ca90bc15c09b1aa33e29c85f52da5a270715ae5b79a', '2024-11-11 14:51:01', 'active', 1, '20241115_113347_photo_6167727085104251083_y.jpg', 0, 'M', '2004-07-06', NULL, NULL, 0),
(22, 'kikay satona', 'kikaysatona@gmail.com', 'scrypt:32768:8:1$m6V2k68IwPeSnkVN$7f46c6b2d4ec36830376b81ec233fa37a929c78a816044db8caf732dba6f2528ec85a9a8f6c51e19aa5d4de0246a1d43779296cae4441b6fb7cf3ab6ac18c8eb', '2024-11-27 14:42:32', 'active', 0, '', 0, NULL, NULL, NULL, NULL, 1),
(23, 'Leotrato Mobile Photography', 'leotratomobilephotography@gmail.com', 'scrypt:32768:8:1$ChWIAI4i0gnKtDxV$173b88938f61b43a227ac5fc00ae38bb056e95fcd29e56a720efb2a451c51fa44e5bcd47f99d940215f7d5f04e74ec5bc598bbedf6f419705d8d76c09c9cce55', '0000-00-00 00:00:00', 'active', 0, 'default.jpg', 0, NULL, NULL, NULL, NULL, 0),
(24, 'janjan fuentes', 'mcdlf@gmail.com', 'scrypt:32768:8:1$j696HUhS25tTSc3J$ab145232d3660616c9ba6439435b01c6c24cfe7e559af2e41f9f751a77b619c7bffffd20810988262872ed6a0a232753d7718609f9238f2f3bd0a6c6967bb424', '2024-12-12 11:57:35', 'active', 0, '', 0, NULL, NULL, NULL, NULL, 1),
(25, 'cyril san antnio', 'cy21@Gmail.com', 'scrypt:32768:8:1$rNgLVxreuVF4TW4D$f826705b58c4278e92dae25f596d5ff06ec93a40705222d421ca923e373f93441906921ab7bc0250778bee26eb9450f1ef209bf51479e5399af161dbe8b7c6da', '2024-12-13 02:41:33', 'active', 0, '', 0, NULL, NULL, NULL, NULL, 1),
(26, 'Teresa Ramos', 'ramosteresa988@gmail.com', 'scrypt:32768:8:1$UU7ObgJIaxcrQnYu$db7b40c130bcc25d857b6763fdde0d868137c8f7926b618b0fac2b32e082747947d6355a420f5d53c82093386fa8b96c4943905d779bc6eaf535184d2d04a69f', '2024-12-27 15:25:34', 'active', 0, '', 0, NULL, NULL, NULL, NULL, 1);

-- --------------------------------------------------------

--
-- Table structure for table `user_details`
--

CREATE TABLE `user_details` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `address` text NOT NULL,
  `city` varchar(50) NOT NULL,
  `barangay` varchar(100) DEFAULT NULL,
  `province` varchar(50) NOT NULL,
  `country` varchar(50) NOT NULL,
  `postcode` varchar(10) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `email` varchar(100) NOT NULL,
  `is_default` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user_details`
--

INSERT INTO `user_details` (`id`, `user_id`, `first_name`, `last_name`, `address`, `city`, `barangay`, `province`, `country`, `postcode`, `phone`, `email`, `is_default`) VALUES
(2, 5, 'marc leo', 'mapanao', 'brgy dos', 'sta cruz', NULL, 'laguna', 'Philippines', '4009', '9123456789', 'marcoleo@gmail.com', 0),
(3, 1, 'joyce', 'ramos', 'purok 1 B', 'Magdalena', 'Balanac', 'Laguna', 'Philippines', '4007', '9053712734', 'joyceramos@gmail.com', 1),
(21, 19, 'marc leo', 'mapanao', 'palasan', 'Magdalena', 'Balanac', 'Laguna', 'Philippines', '4009', '9758079326', 'mleomapanao@gmail.com', 1),
(22, 19, 'marc leo', 'mapanao', 'palasan', 'Magdalena', 'Balanac', 'Laguna', 'Philippines', '4009', '9758079326', 'mleomapanao@gmail.com', 0),
(33, 19, 'marc leo', 'mapanao', 'palasan', 'Magdalena', 'Balanac', 'Laguna', 'Philippines', '4009', '9758079326', 'mleomapanao@gmail.com', 0),
(34, 19, 'marc leo', 'mapanao', 'palasan', 'Magdalena', 'Balanac', 'Laguna', 'Philippines', '4009', '9758079326', 'mleomapanao@gmail.com', 0),
(35, 19, 'marc leo', 'mapanao', 'palasan', 'Magdalena', 'Balanac', 'Laguna', 'Philippines', '4009', '9758079326', 'mleomapanao@gmail.com', 0),
(36, 17, 'kikay', 'ramos', 'purok1b', 'Magdalena', 'Balanac', 'Laguna', 'Philippines', '4007', '9165506792', 'joyceramos270@gmail.com', 1),
(37, 24, 'janjan', 'fuentes', 'ville', 'Santa Cruz', 'Bagumbayan', 'Laguna', 'Philippines', '4009', '9456123789', 'mcdlf@gmail.com', 1),
(39, 25, 'joyce', 'san antnio', 'asdasdasd', 'Kalayaan', 'San Antonio', 'Laguna', 'Philippines', '4015', '9053712734', 'cy21@Gmail.com', 1);

-- --------------------------------------------------------

--
-- Table structure for table `user_details_backup`
--

CREATE TABLE `user_details_backup` (
  `user_id` int(11) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `address` text NOT NULL,
  `city` varchar(50) NOT NULL,
  `province` varchar(50) NOT NULL,
  `country` varchar(50) NOT NULL,
  `postcode` varchar(10) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `email` varchar(100) NOT NULL,
  `is_default` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user_details_backup`
--

INSERT INTO `user_details_backup` (`user_id`, `first_name`, `last_name`, `address`, `city`, `province`, `country`, `postcode`, `phone`, `email`, `is_default`) VALUES
(1, 'joyce', 'ramos', 'barangay balanac', 'magdalena', 'laguna', 'Philippines', '4007', '9053712734', 'joyceramos@gmail.com', 0);

-- --------------------------------------------------------

--
-- Table structure for table `user_logs`
--

CREATE TABLE `user_logs` (
  `log_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `activity_type` varchar(50) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `timestamp` datetime DEFAULT current_timestamp(),
  `action` varchar(250) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user_logs`
--

INSERT INTO `user_logs` (`log_id`, `user_id`, `activity_type`, `description`, `ip_address`, `timestamp`, `action`) VALUES
(1, 4, NULL, 'Admin login', '127.0.0.1', '2024-11-30 19:43:17', 'LOGIN'),
(2, 4, NULL, 'Updated profile information', '127.0.0.1', '2024-11-30 19:43:17', 'PROFILE_UPDATE'),
(3, 1, NULL, 'User login', '127.0.0.1', '2024-11-30 19:43:17', 'LOGIN'),
(4, 1, NULL, 'Placed order #123', '127.0.0.1', '2024-11-30 19:43:17', 'ORDER'),
(5, 1, NULL, 'User logged out', '127.0.0.1', '2024-12-12 16:59:28', 'LOGOUT'),
(6, 1, NULL, 'User logged out', '127.0.0.1', '2024-12-12 17:02:31', 'LOGOUT'),
(7, 1, NULL, 'User logged out', '127.0.0.1', '2024-12-13 06:51:01', 'LOGOUT'),
(8, 1, NULL, 'User logged out', '127.0.0.1', '2024-12-13 07:20:40', 'LOGOUT'),
(9, 17, NULL, 'User logged out', '127.0.0.1', '2024-12-13 07:29:31', 'LOGOUT'),
(10, 24, NULL, 'User logged out', '127.0.0.1', '2024-12-13 07:31:55', 'LOGOUT'),
(11, 17, NULL, 'User logged out', '127.0.0.1', '2024-12-13 09:59:25', 'LOGOUT'),
(12, 1, NULL, 'User logged out', '127.0.0.1', '2024-12-13 10:39:50', 'LOGOUT'),
(13, 24, NULL, 'User logged out', '127.0.0.1', '2024-12-13 10:49:43', 'LOGOUT'),
(14, 25, NULL, 'User logged out', '127.0.0.1', '2024-12-13 10:58:43', 'LOGOUT'),
(15, 17, NULL, 'User logged out', '127.0.0.1', '2024-12-13 11:22:36', 'LOGOUT'),
(16, 1, NULL, 'User logged out', '127.0.0.1', '2024-12-13 11:46:42', 'LOGOUT'),
(17, 17, NULL, 'User logged out', '127.0.0.1', '2024-12-13 11:51:41', 'LOGOUT'),
(18, 17, NULL, 'User logged out', '127.0.0.1', '2024-12-13 11:55:35', 'LOGOUT'),
(19, 1, NULL, 'User logged out', '127.0.0.1', '2024-12-27 22:40:40', 'LOGOUT'),
(20, 1, NULL, 'User logged out', '127.0.0.1', '2024-12-27 23:17:46', 'LOGOUT'),
(21, 1, NULL, 'User logged out', '127.0.0.1', '2024-12-27 23:19:09', 'LOGOUT'),
(22, 1, NULL, 'User logged out', '127.0.0.1', '2024-12-27 23:22:09', 'LOGOUT'),
(23, 26, NULL, 'User logged out', '127.0.0.1', '2024-12-27 23:46:23', 'LOGOUT'),
(24, 1, NULL, 'User logged out', '127.0.0.1', '2024-12-27 23:47:57', 'LOGOUT'),
(25, 17, NULL, 'User logged out', '127.0.0.1', '2024-12-27 23:48:35', 'LOGOUT'),
(26, 1, NULL, 'User logged out', '127.0.0.1', '2025-01-01 22:44:13', 'LOGOUT'),
(27, 1, NULL, 'User logged out', '127.0.0.1', '2025-01-02 21:43:55', 'LOGOUT'),
(28, 1, NULL, 'User logged out', '127.0.0.1', '2025-01-02 22:09:54', 'LOGOUT'),
(29, 1, NULL, 'User logged out', '127.0.0.1', '2025-02-12 20:04:20', 'LOGOUT');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `bank_accounts`
--
ALTER TABLE `bank_accounts`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `bank_details`
--
ALTER TABLE `bank_details`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `cart`
--
ALTER TABLE `cart`
  ADD PRIMARY KEY (`cart_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `product_id` (`product_id`);

--
-- Indexes for table `chat_messages`
--
ALTER TABLE `chat_messages`
  ADD PRIMARY KEY (`message_id`),
  ADD KEY `reply_to_message_id` (`reply_to_message_id`);

--
-- Indexes for table `couriers`
--
ALTER TABLE `couriers`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `favorites`
--
ALTER TABLE `favorites`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `product_id` (`product_id`);

--
-- Indexes for table `inventory`
--
ALTER TABLE `inventory`
  ADD PRIMARY KEY (`inventory_id`),
  ADD KEY `product_id` (`product_id`),
  ADD KEY `seller_id` (`seller_id`);

--
-- Indexes for table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`notification_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `order_id` (`order_id`);

--
-- Indexes for table `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`order_id`),
  ADD KEY `buyer_id` (`buyer_id`);

--
-- Indexes for table `order_items`
--
ALTER TABLE `order_items`
  ADD PRIMARY KEY (`order_item_id`),
  ADD KEY `order_id` (`order_id`),
  ADD KEY `product_id` (`product_id`);

--
-- Indexes for table `payments`
--
ALTER TABLE `payments`
  ADD PRIMARY KEY (`payment_id`),
  ADD KEY `order_id` (`order_id`);

--
-- Indexes for table `payment_methods`
--
ALTER TABLE `payment_methods`
  ADD PRIMARY KEY (`payment_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`product_id`),
  ADD KEY `fk_seller` (`seller_id`);

--
-- Indexes for table `related_products`
--
ALTER TABLE `related_products`
  ADD PRIMARY KEY (`product_id`,`related_product_id`),
  ADD KEY `related_product_id` (`related_product_id`);

--
-- Indexes for table `reviews`
--
ALTER TABLE `reviews`
  ADD PRIMARY KEY (`review_id`),
  ADD KEY `product_id` (`product_id`),
  ADD KEY `buyer_id` (`buyer_id`);

--
-- Indexes for table `seller_requests`
--
ALTER TABLE `seller_requests`
  ADD PRIMARY KEY (`request_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `username` (`name`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `user_details`
--
ALTER TABLE `user_details`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `user_logs`
--
ALTER TABLE `user_logs`
  ADD PRIMARY KEY (`log_id`),
  ADD KEY `user_id` (`user_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `bank_accounts`
--
ALTER TABLE `bank_accounts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `bank_details`
--
ALTER TABLE `bank_details`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `cart`
--
ALTER TABLE `cart`
  MODIFY `cart_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=115;

--
-- AUTO_INCREMENT for table `chat_messages`
--
ALTER TABLE `chat_messages`
  MODIFY `message_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=57;

--
-- AUTO_INCREMENT for table `couriers`
--
ALTER TABLE `couriers`
  MODIFY `id` int(50) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `favorites`
--
ALTER TABLE `favorites`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `inventory`
--
ALTER TABLE `inventory`
  MODIFY `inventory_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `notification_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=174;

--
-- AUTO_INCREMENT for table `orders`
--
ALTER TABLE `orders`
  MODIFY `order_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=91;

--
-- AUTO_INCREMENT for table `order_items`
--
ALTER TABLE `order_items`
  MODIFY `order_item_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=94;

--
-- AUTO_INCREMENT for table `payments`
--
ALTER TABLE `payments`
  MODIFY `payment_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `payment_methods`
--
ALTER TABLE `payment_methods`
  MODIFY `payment_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `products`
--
ALTER TABLE `products`
  MODIFY `product_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=37;

--
-- AUTO_INCREMENT for table `reviews`
--
ALTER TABLE `reviews`
  MODIFY `review_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `seller_requests`
--
ALTER TABLE `seller_requests`
  MODIFY `request_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- AUTO_INCREMENT for table `user_details`
--
ALTER TABLE `user_details`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=40;

--
-- AUTO_INCREMENT for table `user_logs`
--
ALTER TABLE `user_logs`
  MODIFY `log_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=30;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `bank_accounts`
--
ALTER TABLE `bank_accounts`
  ADD CONSTRAINT `bank_accounts_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `bank_details`
--
ALTER TABLE `bank_details`
  ADD CONSTRAINT `bank_details_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `cart`
--
ALTER TABLE `cart`
  ADD CONSTRAINT `cart_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `cart_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`) ON DELETE CASCADE;

--
-- Constraints for table `chat_messages`
--
ALTER TABLE `chat_messages`
  ADD CONSTRAINT `chat_messages_ibfk_1` FOREIGN KEY (`reply_to_message_id`) REFERENCES `chat_messages` (`message_id`) ON DELETE SET NULL;

--
-- Constraints for table `favorites`
--
ALTER TABLE `favorites`
  ADD CONSTRAINT `favorites_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  ADD CONSTRAINT `favorites_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`);

--
-- Constraints for table `inventory`
--
ALTER TABLE `inventory`
  ADD CONSTRAINT `inventory_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`),
  ADD CONSTRAINT `inventory_ibfk_2` FOREIGN KEY (`seller_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  ADD CONSTRAINT `notifications_ibfk_2` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`);

--
-- Constraints for table `orders`
--
ALTER TABLE `orders`
  ADD CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`buyer_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `order_items`
--
ALTER TABLE `order_items`
  ADD CONSTRAINT `order_items_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `order_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`) ON DELETE CASCADE;

--
-- Constraints for table `payments`
--
ALTER TABLE `payments`
  ADD CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`) ON DELETE CASCADE;

--
-- Constraints for table `payment_methods`
--
ALTER TABLE `payment_methods`
  ADD CONSTRAINT `payment_methods_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `products`
--
ALTER TABLE `products`
  ADD CONSTRAINT `fk_seller` FOREIGN KEY (`seller_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `related_products`
--
ALTER TABLE `related_products`
  ADD CONSTRAINT `related_products_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`),
  ADD CONSTRAINT `related_products_ibfk_2` FOREIGN KEY (`related_product_id`) REFERENCES `products` (`product_id`);

--
-- Constraints for table `reviews`
--
ALTER TABLE `reviews`
  ADD CONSTRAINT `reviews_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`),
  ADD CONSTRAINT `reviews_ibfk_2` FOREIGN KEY (`buyer_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `seller_requests`
--
ALTER TABLE `seller_requests`
  ADD CONSTRAINT `seller_requests_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `user_details`
--
ALTER TABLE `user_details`
  ADD CONSTRAINT `user_details_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `user_logs`
--
ALTER TABLE `user_logs`
  ADD CONSTRAINT `user_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
