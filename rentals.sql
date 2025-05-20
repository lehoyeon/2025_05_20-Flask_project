USE test;  

-- 테이블 생성
-- 물품목록
CREATE TABLE items (
  item_id      INT PRIMARY KEY AUTO_INCREMENT,
  name         VARCHAR(100) NOT NULL,
  price        INT NOT NULL,
  quantity     INT DEFAULT 1,
  created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
);   

-- 사용자 정보
CREATE TABLE users (
  user_id    INT PRIMARY KEY AUTO_INCREMENT,
  name       VARCHAR(100) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 대여 내역
CREATE TABLE rentals (
  rental_id     INT PRIMARY KEY AUTO_INCREMENT,
  user_id       INT NOT NULL,
  item_id       INT NOT NULL,
  rent_date     DATE NOT NULL DEFAULT CURRENT_DATE,
  return_date   DATE,
  due_date      DATE,
  status        VARCHAR(20) DEFAULT '대여중',  -- 대여중, 반납 완료, 연체 등
  price         INT, -- 대여 금액 (단가 기준)
  FOREIGN KEY (user_id) REFERENCES users(user_id),
  FOREIGN KEY (item_id) REFERENCES items(item_id)
);