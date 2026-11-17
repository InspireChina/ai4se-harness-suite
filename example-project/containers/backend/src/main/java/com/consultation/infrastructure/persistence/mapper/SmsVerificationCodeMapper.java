package com.consultation.infrastructure.persistence.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.consultation.infrastructure.persistence.po.SmsVerificationCodePO;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface SmsVerificationCodeMapper extends BaseMapper<SmsVerificationCodePO> {
}
