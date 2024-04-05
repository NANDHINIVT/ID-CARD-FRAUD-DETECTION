-- phpMyAdmin SQL Dump
-- version 2.11.6
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Jan 18, 2024 at 11:53 AM
-- Server version: 5.0.51
-- PHP Version: 5.2.6

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `idcard`
--

-- --------------------------------------------------------

--
-- Table structure for table `sf_admin`
--

CREATE TABLE `sf_admin` (
  `username` varchar(20) NOT NULL,
  `password` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `sf_admin`
--

INSERT INTO `sf_admin` (`username`, `password`) VALUES
('admin', 'admin');

-- --------------------------------------------------------

--
-- Table structure for table `sf_files`
--

CREATE TABLE `sf_files` (
  `id` int(11) NOT NULL,
  `uname` varchar(20) NOT NULL,
  `filename` varchar(50) NOT NULL,
  `mobile` bigint(20) NOT NULL,
  `email` varchar(40) NOT NULL,
  `rdate` varchar(15) NOT NULL,
  `name` varchar(40) NOT NULL,
  `dob` varchar(20) NOT NULL,
  `gender` varchar(10) NOT NULL,
  `aadhar` varchar(20) NOT NULL,
  `ctype` varchar(20) NOT NULL,
  `filename2` varchar(50) NOT NULL,
  `address` varchar(200) NOT NULL,
  `value1` varchar(100) NOT NULL,
  `value2` varchar(200) NOT NULL,
  `value3` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `sf_files`
--

INSERT INTO `sf_files` (`id`, `uname`, `filename`, `mobile`, `email`, `rdate`, `name`, `dob`, `gender`, `aadhar`, `ctype`, `filename2`, `address`, `value1`, `value2`, `value3`) VALUES
(1, 'Manimaran', 'F1a2.jpg', 8954455622, 'manimaran@gmail.com', '18-11-2023', 'Manimaran Ramachandran ', '03/09/1967', 'MALE', '3515 0558 6323 ', 'Aadhar', 'B1a21.jpg', 'S/O: Ramachandran, 3/256 A, MAIN ROAD, realy. Thiruvarur, Tamil Nadu - 614702', '', '', ''),
(2, 'Dayashankar', 'F2p1.jpg', 8742266996, 'daya@gmail.com', '18-11-2023', 'DAYASHANKAR MISHRA ', '10/10/1994 ', '', 'CLUPM0440B ', 'Pancard', '', '', '', '', ''),
(3, 'Lakshmi', 'F3a5.jpg', 8956254522, 'lakshmi@gmail.com', '05-12-2023', 'Lakshmi B ', '21/05/1973', 'FEMALE', '3314 5055 2188 ', 'Aadhar', 'B3a51.jpg', '3162, NORTH STREET, PRAMASAMYPURAM, Pappakudl, Virudhunagar, Tamil Nadu - 626134 udmsBonid we 3000 40', '', '', ''),
(4, 'Vanitha', 'F4cert5.jpg', 8956454212, 'vanitha@gmail.com', '05-12-2023', '', '', '', '', 'Certificate', '', '', 'Folio No.:AUTCE005564 1a qualified for the award ', 'Name Registration Number Degree BranchiSpecialization Month and Year of Passing Classification ‘VANITHA M ‘13410104060(1026495) BE. ‘Computer Science and Engineering April 2044 FIRSTCLASS ', '»)) Dale: rgusruta Nis pote ');

-- --------------------------------------------------------

--
-- Table structure for table `sf_register`
--

CREATE TABLE `sf_register` (
  `id` int(11) NOT NULL,
  `name` varchar(20) NOT NULL,
  `mobile` bigint(20) NOT NULL,
  `email` varchar(40) NOT NULL,
  `uname` varchar(20) NOT NULL,
  `pass` varchar(20) NOT NULL,
  PRIMARY KEY  (`uname`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `sf_register`
--

INSERT INTO `sf_register` (`id`, `name`, `mobile`, `email`, `uname`, `pass`) VALUES
(1, 'Dinesh', 8956234546, 'dinesh@gmail.com', 'dinesh', '1234');
